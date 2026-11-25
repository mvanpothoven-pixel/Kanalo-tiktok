// AssistantView.swift — chat met de AI-assistent (Grok via jouw eigen server).
// Werkt in Kanalo én TableJoy; zelfde bestand in beide Xcode-projecten.
//
// In de app staat GEEN xAI-sleutel. De app kent alleen:
//   - AssistantBaseURL  (Info.plist) bv. https://assistent.jouwdomein.nl
//   - AssistantToken    (Info.plist) het app-token (KANALO_TOKEN of TABLEJOY_TOKEN)
// Zet die twee in een .xcconfig die niet in git staat (zie README).
//
// Instellingen:
//   NavigationLink { AssistantView(app: .kanalo, deviceID: Device.id) } label: {
//       Label("Assistent", systemImage: "sparkles")
//   }

import SwiftUI

enum AssistantApp: String {
    case kanalo, tablejoy

    var title: String { self == .kanalo ? "Kanalo-assistent" : "TableJoy-assistent" }
    var greeting: String {
        switch self {
        case .kanalo:
            return "Hoi! Ik help je met je playlist, de gids, afspelen en je abonnement. Kanalo is een speler: de zenders komen uit je eigen M3U- of Xtream-playlist."
        case .tablejoy:
            return "Hoi! Vraag me naar je reserveringen, bijvoorbeeld: wie komt er vanavond?"
        }
    }
    var suggestions: [String] {
        switch self {
        case .kanalo: return ["Hoe voeg ik mijn playlist toe?", "Mijn gids is leeg", "Wat is mijn abonnementsstatus?"]
        case .tablejoy: return ["Welke reserveringen hebben we vanavond?", "Zijn er grote groepen deze week?"]
        }
    }
}

struct AssistantMessage: Identifiable, Equatable {
    enum Role: String { case user, assistant }
    let id = UUID()
    let role: Role
    let text: String
}

// MARK: - Netwerk

struct AssistantClient {
    let app: AssistantApp
    /// Kanalo: het device-ID dat de app ook voor bugrapporten gebruikt.
    var deviceID: String?
    /// TableJoy: het restaurant van de ingelogde gebruiker.
    var restaurantID: String?

    struct Reply: Decodable { let reply: String; let demo_data: Bool? }
    struct ServerError: Decodable { let error: String }

    enum Failure: LocalizedError {
        case notConfigured, server(String), http(Int)
        var errorDescription: String? {
            switch self {
            case .notConfigured: return "De assistent is nog niet ingesteld in deze build."
            case .server(let m): return m
            case .http(let c): return "De assistent is even niet bereikbaar (\(c))."
            }
        }
    }

    private var baseURL: URL? {
        (Bundle.main.object(forInfoDictionaryKey: "AssistantBaseURL") as? String)
            .flatMap { $0.isEmpty ? nil : URL(string: $0) }
    }
    private var token: String? {
        (Bundle.main.object(forInfoDictionaryKey: "AssistantToken") as? String).flatMap { $0.isEmpty ? nil : $0 }
    }

    func send(_ history: [AssistantMessage]) async throws -> Reply {
        guard let baseURL, let token else { throw Failure.notConfigured }
        var req = URLRequest(url: baseURL.appendingPathComponent("assistant"))
        req.httpMethod = "POST"
        req.timeoutInterval = 90
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        if let deviceID { req.setValue(deviceID, forHTTPHeaderField: "X-Device-Id") }
        if let restaurantID { req.setValue(restaurantID, forHTTPHeaderField: "X-Restaurant-Id") }
        let messages = history.suffix(20).map { ["role": $0.role.rawValue, "content": $0.text] }
        req.httpBody = try JSONSerialization.data(withJSONObject: ["app": app.rawValue, "messages": messages])

        let (data, response) = try await URLSession.shared.data(for: req)
        let status = (response as? HTTPURLResponse)?.statusCode ?? 0
        guard status == 200 else {
            if let e = try? JSONDecoder().decode(ServerError.self, from: data) { throw Failure.server(e.error) }
            throw Failure.http(status)
        }
        return try JSONDecoder().decode(Reply.self, from: data)
    }
}

// MARK: - View

@MainActor
final class AssistantModel: ObservableObject {
    @Published var messages: [AssistantMessage] = []
    @Published var input = ""
    @Published var isSending = false
    @Published var errorText: String?
    let client: AssistantClient

    init(client: AssistantClient) { self.client = client }

    func send(_ text: String? = nil) async {
        let question = (text ?? input).trimmingCharacters(in: .whitespacesAndNewlines)
        guard !question.isEmpty, !isSending else { return }
        input = ""
        errorText = nil
        messages.append(.init(role: .user, text: question))
        isSending = true
        defer { isSending = false }
        do {
            let r = try await client.send(messages)
            messages.append(.init(role: .assistant, text: r.reply))
        } catch {
            errorText = error.localizedDescription
        }
    }
}

struct AssistantView: View {
    let app: AssistantApp
    @StateObject private var model: AssistantModel
    @FocusState private var focused: Bool

    init(app: AssistantApp, deviceID: String? = nil, restaurantID: String? = nil) {
        self.app = app
        _model = StateObject(wrappedValue: AssistantModel(client: AssistantClient(app: app, deviceID: deviceID, restaurantID: restaurantID)))
    }

    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 12) {
                        bubble(AssistantMessage(role: .assistant, text: app.greeting))
                        if model.messages.isEmpty {
                            ForEach(app.suggestions, id: \.self) { s in
                                Button(s) { Task { await model.send(s) } }
                                    .buttonStyle(.bordered)
                            }
                        }
                        ForEach(model.messages) { bubble($0).id($0.id) }
                        if model.isSending {
                            ProgressView().padding(.leading, 8).id("loading")
                        }
                        if let e = model.errorText {
                            Text(e).font(.footnote).foregroundStyle(.red)
                        }
                    }
                    .padding()
                }
                .onChange(of: model.messages) { _ in
                    withAnimation { proxy.scrollTo(model.messages.last?.id, anchor: .bottom) }
                }
            }
            Divider()
            HStack(alignment: .bottom, spacing: 8) {
                TextField("Stel je vraag…", text: $model.input, axis: .vertical)
                    .lineLimit(1...5)
                    .textFieldStyle(.roundedBorder)
                    .focused($focused)
                    .submitLabel(.send)
                    .onSubmit { Task { await model.send() } }
                Button {
                    Task { await model.send() }
                } label: {
                    Image(systemName: "arrow.up.circle.fill").font(.title2)
                }
                .disabled(model.input.trimmingCharacters(in: .whitespaces).isEmpty || model.isSending)
                .accessibilityLabel("Verstuur")
            }
            .padding()
        }
        .navigationTitle(app.title)
        #if os(iOS)
        .navigationBarTitleDisplayMode(.inline)
        #endif
    }

    @ViewBuilder
    private func bubble(_ m: AssistantMessage) -> some View {
        HStack {
            if m.role == .user { Spacer(minLength: 40) }
            Text(m.text)
                .textSelection(.enabled)
                .padding(12)
                .background(m.role == .user ? Color.accentColor.opacity(0.18) : Color.secondary.opacity(0.12))
                .clipShape(RoundedRectangle(cornerRadius: 14))
            if m.role == .assistant { Spacer(minLength: 40) }
        }
    }
}
