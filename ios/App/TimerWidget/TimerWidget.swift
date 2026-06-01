import WidgetKit
import SwiftUI

private let appGroup = "group.com.sauuri.nozeroday"

struct TimerEntry: TimelineEntry {
    let date: Date
    let endTime: Date?
    let label: String
}

struct TimerProvider: TimelineProvider {
    func placeholder(in context: Context) -> TimerEntry {
        TimerEntry(date: .now, endTime: Date().addingTimeInterval(60), label: "벤치프레스")
    }
    func getSnapshot(in context: Context, completion: @escaping (TimerEntry) -> Void) {
        completion(makeEntry())
    }
    func getTimeline(in context: Context, completion: @escaping (Timeline<TimerEntry>) -> Void) {
        let entry = makeEntry()
        let refresh = entry.endTime.map { max($0, Date().addingTimeInterval(60)) } ?? Date().addingTimeInterval(300)
        completion(Timeline(entries: [entry], policy: .after(refresh)))
    }
    private func makeEntry() -> TimerEntry {
        let d = UserDefaults(suiteName: appGroup)
        let ms = d?.double(forKey: "timerEndTime") ?? 0
        let label = d?.string(forKey: "timerLabel") ?? ""
        let end: Date? = ms > 0 ? Date(timeIntervalSince1970: ms / 1000) : nil
        return TimerEntry(date: .now, endTime: end.flatMap { $0 > .now ? $0 : nil }, label: label)
    }
}

struct TimerWidgetView: View {
    let entry: TimerEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        ZStack {
            Color(red: 0.02, green: 0.03, blue: 0.06)
            if let end = entry.endTime {
                VStack(spacing: 3) {
                    Text("💪 NO ZERO DAY")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundColor(.white.opacity(0.45))
                        .kerning(1.2)
                    Text(end, style: .timer)
                        .font(.system(size: family == .systemSmall ? 36 : 44, weight: .black, design: .rounded))
                        .foregroundColor(Color(red: 0.06, green: 0.73, blue: 0.60))
                        .monospacedDigit()
                        .minimumScaleFactor(0.7)
                    Text("휴식 타이머")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundColor(.white.opacity(0.35))
                    if !entry.label.isEmpty {
                        Text(entry.label)
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.white.opacity(0.7))
                            .lineLimit(1)
                    }
                }
                .padding(10)
            } else {
                VStack(spacing: 6) {
                    Text("💪")
                        .font(.system(size: 28))
                    Text("No Zero Day")
                        .font(.system(size: 13, weight: .bold))
                        .foregroundColor(.white)
                    Text("휴식 타이머 없음")
                        .font(.system(size: 10))
                        .foregroundColor(.white.opacity(0.4))
                }
            }
        }
        .containerBackground(Color(red: 0.02, green: 0.03, blue: 0.06), for: .widget)
    }
}

struct TimerWidget: Widget {
    let kind = "NZDTimer"
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: TimerProvider()) { entry in
            TimerWidgetView(entry: entry)
        }
        .configurationDisplayName("NZD 휴식 타이머")
        .description("운동 세트 간 휴식 타이머를 홈 화면에서 확인하세요.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
