import SwiftUI

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()
    @State private var searchText = ""
    @State private var selectedMode = "hybrid"
    
    let searchModes = ["hybrid", "semantic", "keyword", "code_similarity"]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Search Bar
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.secondary)
                    
                    TextField("Search knowledge base...", text: $searchText)
                        .textFieldStyle(PlainTextFieldStyle())
                        .onSubmit {
                            Task {
                                await viewModel.search(query: searchText, mode: selectedMode)
                            }
                        }
                    
                    if !searchText.isEmpty {
                        Button(action: { searchText = "" }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.secondary)
                        }
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(10)
                .padding(.horizontal)
                .padding(.top, 8)
                
                // Mode Picker
                Picker("Search Mode", selection: $selectedMode) {
                    ForEach(searchModes, id: \.self) { mode in
                        Text(mode.capitalized).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)
                .padding(.vertical, 8)
                
                // Results
                if viewModel.isLoading {
                    ProgressView("Searching...")
                        .frame(maxHeight: .infinity)
                } else if viewModel.results.isEmpty && !searchText.isEmpty {
                    ContentUnavailableView(
                        "No Results",
                        systemImage: "magnifyingglass",
                        description: Text("Try a different search term or mode")
                    )
                } else {
                    List(viewModel.results) { result in
                        SearchResultRow(result: result)
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("Search")
        }
    }
}

// MARK: - Search Result Row
struct SearchResultRow: View {
    let result: QueryResult
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: iconForType(result.entry.sourceType))
                    .foregroundColor(.blue)
                Text(result.entry.sourceType.capitalized)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Text(String(format: "%.2f", result.score))
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(scoreColor(result.score).opacity(0.2))
                    .cornerRadius(4)
            }
            
            Text(result.entry.content.prefix(150))
                .font(.body)
                .lineLimit(4)
            
            if let sourcePath = result.entry.sourcePath {
                Text(sourcePath)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
        }
        .padding(.vertical, 4)
    }
    
    private func iconForType(_ type: String) -> String {
        switch type {
        case "markdown": return "doc.richtext"
        case "code": return "chevron.left.forwardslash.chevron.right"
        case "pdf": return "doc.richtext"
        case "html": return "globe"
        default: return "doc"
        }
    }
    
    private func scoreColor(_ score: Double) -> Color {
        if score >= 0.7 { return .green }
        if score >= 0.4 { return .orange }
        return .red
    }
}

// MARK: - Search View Model
@MainActor
class SearchViewModel: ObservableObject {
    @Published var results: [QueryResult] = []
    @Published var isLoading = false
    @Published var error: String?
    
    private let apiService = APIService.shared
    
    func search(query: String, mode: String) async {
        guard !query.isEmpty else { return }
        
        isLoading = true
        error = nil
        
        do {
            results = try await apiService.queryKnowledge(text: query, mode: mode)
        } catch {
            self.error = error.localizedDescription
        }
        
        isLoading = false
    }
}

#Preview {
    SearchView()
}
