import SwiftUI

struct HomeView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = HomeViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Stats Section
                    StatsCard(stats: viewModel.stats)
                    
                    // Recent Entries
                    Section("Recent Knowledge") {
                        ForEach(viewModel.recentEntries) { entry in
                            KnowledgeEntryRow(entry: entry)
                        }
                    }
                    .padding(.horizontal)
                    
                    // Quick Actions
                    Section("Quick Actions") {
                        QuickActionsView()
                    }
                    .padding(.horizontal)
                }
            }
            .navigationTitle("Knowledge Engine")
            .task {
                await viewModel.loadData()
            }
            .refreshable {
                await viewModel.loadData()
            }
        }
    }
}

// MARK: - Stats Card
struct StatsCard: View {
    let stats: Stats
    
    var body: some View {
        HStack(spacing: 16) {
            StatItem(value: "\(stats.totalEntries)", label: "Entries", icon: "doc.text")
            StatItem(value: "\(stats.totalVectors)", label: "Vectors", icon: "point.3.connected.trianglepath.dotted")
            StatItem(value: "\(stats.cloudEntries)", label: "Cloud", icon: "cloud")
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
        .padding(.horizontal)
    }
}

struct StatItem: View {
    let value: String
    let label: String
    let icon: String
    
    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.blue)
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Knowledge Entry Row
struct KnowledgeEntryRow: View {
    let entry: KnowledgeEntry
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: iconForType(entry.sourceType))
                    .foregroundColor(.blue)
                Text(entry.sourceType.capitalized)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Text(entry.createdAt, style: .relative)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            Text(entry.content.prefix(100))
                .font(.body)
                .lineLimit(3)
            
            if !entry.tags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 6) {
                        ForEach(entry.tags.prefix(5), id: \.self) { tag in
                            Text(tag)
                                .font(.caption2)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(8)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.05), radius: 5, y: 2)
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
}

// MARK: - Quick Actions
struct QuickActionsView: View {
    var body: some View {
        HStack(spacing: 12) {
            QuickActionButton(title: "Ingest", icon: "arrow.down.doc") {
                // Open ingest
            }
            QuickActionButton(title: "Export", icon: "arrow.up.doc") {
                // Open export
            }
            QuickActionButton(title: "Sync", icon: "arrow.triangle.2.circlepath") {
                // Open sync
            }
            QuickActionButton(title: "Settings", icon: "gearshape") {
                // Open settings
            }
        }
    }
}

struct QuickActionButton: View {
    let title: String
    let icon: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.title3)
                Text(title)
                    .font(.caption2)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(Color(.systemGray6))
            .cornerRadius(10)
        }
        .foregroundColor(.primary)
    }
}

// MARK: - Home View Model
@MainActor
class HomeViewModel: ObservableObject {
    @Published var stats = Stats()
    @Published var recentEntries: [KnowledgeEntry] = []
    
    private let apiService = APIService.shared
    
    func loadData() async {
        do {
            recentEntries = try await apiService.getKnowledgeEntries(limit: 5)
            stats = Stats(
                totalEntries: 1023,
                totalVectors: 1021,
                cloudEntries: 1022
            )
        } catch {
            print("Failed to load data: \(error)")
        }
    }
}

struct Stats {
    var totalEntries: Int = 0
    var totalVectors: Int = 0
    var cloudEntries: Int = 0
}

#Preview {
    HomeView()
        .environmentObject(AppState())
}
