import SwiftUI

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    @State private var messageText = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Messages
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(viewModel.messages) { message in
                                MessageBubble(message: message)
                                    .id(message.id)
                            }
                            
                            if viewModel.isLoading {
                                TypingIndicator()
                            }
                        }
                        .padding()
                    }
                    .onChange(of: viewModel.messages.count) { _ in
                        withAnimation {
                            proxy.scrollTo(viewModel.messages.last?.id, anchor: .bottom)
                        }
                    }
                }
                
                // Input
                HStack(spacing: 12) {
                    TextField("Ask anything...", text: $messageText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .onSubmit {
                            sendMessage()
                        }
                    
                    Button(action: sendMessage) {
                        Image(systemName: "arrow.up.circle.fill")
                            .font(.title2)
                            .foregroundColor(messageText.isEmpty ? .gray : .blue)
                    }
                    .disabled(messageText.isEmpty || viewModel.isLoading)
                }
                .padding()
                .background(Color(.systemBackground))
            }
            .navigationTitle("Chat")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private func sendMessage() {
        let text = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        
        messageText = ""
        Task {
            await viewModel.sendMessage(text)
        }
    }
}

// MARK: - Message Bubble
struct MessageBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.role == .user { Spacer(minLength: 60) }
            
            VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(message.role == .user ? Color.blue : Color(.systemGray5))
                    .foregroundColor(message.role == .user ? .white : .primary)
                    .cornerRadius(16)
                
                Text(message.timestamp, style: .time)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .padding(.horizontal, 4)
            }
            
            if message.role == .assistant { Spacer(minLength: 60) }
        }
    }
}

// MARK: - Typing Indicator
struct TypingIndicator: View {
    @State private var dots = 0
    
    var body: some View {
        HStack {
            HStack(spacing: 4) {
                ForEach(0..<3, id: \.self) { index in
                    Circle()
                        .fill(Color.gray)
                        .frame(width: 8, height: 8)
                        .scaleEffect(dots == index ? 1.2 : 0.8)
                        .animation(
                            .easeInOut(duration: 0.5)
                            .repeatForever(autoreverses: true)
                            .delay(Double(index) * 0.15),
                            value: dots
                        )
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(Color(.systemGray5))
            .cornerRadius(16)
            
            Spacer()
        }
        .onAppear {
            withAnimation {
                dots = 2
            }
        }
    }
}

// MARK: - Chat View Model
@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isLoading = false
    @Published var error: String?
    
    private let apiService = APIService.shared
    
    func sendMessage(_ text: String) async {
        // Add user message
        let userMessage = ChatMessage(role: .user, content: text, timestamp: Date())
        messages.append(userMessage)
        
        isLoading = true
        
        do {
            // Prepare history
            let history: [[String: String]] = messages.map { msg in
                ["role": msg.role.rawValue, "content": msg.content]
            }
            
            // Get response
            let response = try await apiService.sendChatMessage(text, history: history)
            
            // Add assistant message
            let assistantMessage = ChatMessage(role: .assistant, content: response, timestamp: Date())
            messages.append(assistantMessage)
        } catch {
            self.error = error.localizedDescription
            let errorMessage = ChatMessage(role: .assistant, content: "Sorry, I encountered an error: \(error.localizedDescription)", timestamp: Date())
            messages.append(errorMessage)
        }
        
        isLoading = false
    }
}

#Preview {
    ChatView()
}
