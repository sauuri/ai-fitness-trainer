import ActivityKit
import SwiftUI
import TimerShared
import WidgetKit

private let orange = Color(red: 0.976, green: 0.451, blue: 0.086)

private func fmtElapsed(_ secs: Int) -> String {
    let h = secs / 3600
    let m = (secs % 3600) / 60
    let s = secs % 60
    if h > 0 {
        return String(format: "%d:%02d:%02d", h, m, s)
    }
    return String(format: "%02d:%02d", m, s)
}

struct WorkoutLiveActivityView: View {
    let context: ActivityViewContext<TimerActivityAttributes>

    var body: some View {
        HStack(alignment: .center, spacing: 0) {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 0) {
                    Text("No ").font(.system(size: 15, weight: .black)).foregroundColor(.white)
                    Text("Zero").font(.system(size: 15, weight: .black)).foregroundColor(orange)
                    Text(" Day").font(.system(size: 15, weight: .black)).foregroundColor(.white)
                }
                Text("총 운동시간")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.white.opacity(0.45))
                    .kerning(0.5)
            }
            .padding(.leading, 20)

            Spacer()

            Group {
                if context.state.isPaused {
                    Text(fmtElapsed(context.state.elapsedSeconds))
                        .font(.system(size: 38, weight: .black, design: .rounded))
                        .foregroundColor(.white.opacity(0.5))
                        .monospacedDigit()
                } else {
                    Text(context.state.startTime, style: .timer)
                        .font(.system(size: 38, weight: .black, design: .rounded))
                        .foregroundColor(.white)
                        .monospacedDigit()
                        .minimumScaleFactor(0.8)
                }
            }
            .padding(.trailing, 8)
        }
        .padding(.vertical, 14)
        .activityBackgroundTint(Color(red: 0.03, green: 0.03, blue: 0.04))
    }
}

struct WorkoutLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: TimerActivityAttributes.self) { context in
            WorkoutLiveActivityView(context: context)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    HStack(spacing: 0) {
                        Text("No ").font(.system(size: 13, weight: .black)).foregroundColor(.white)
                        Text("Zero").font(.system(size: 13, weight: .black)).foregroundColor(orange)
                        Text(" Day").font(.system(size: 13, weight: .black)).foregroundColor(.white)
                    }
                }
                DynamicIslandExpandedRegion(.trailing) {
                    if context.state.isPaused {
                        Text(fmtElapsed(context.state.elapsedSeconds))
                            .font(.system(size: 20, weight: .black, design: .rounded))
                            .foregroundColor(.white.opacity(0.5))
                            .monospacedDigit()
                    } else {
                        Text(context.state.startTime, style: .timer)
                            .font(.system(size: 20, weight: .black, design: .rounded))
                            .foregroundColor(.white)
                            .monospacedDigit()
                    }
                }
                DynamicIslandExpandedRegion(.bottom) {
                    Text(context.state.isPaused ? "일시정지" : "총 운동시간")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.white.opacity(0.4))
                }
            } compactLeading: {
                Text("NZD").font(.system(size: 10, weight: .black)).foregroundColor(orange)
            } compactTrailing: {
                if context.state.isPaused {
                    Text(fmtElapsed(context.state.elapsedSeconds))
                        .font(.system(size: 12, weight: .bold, design: .rounded))
                        .foregroundColor(.white.opacity(0.5))
                        .monospacedDigit()
                        .frame(maxWidth: 55)
                } else {
                    Text(context.state.startTime, style: .timer)
                        .font(.system(size: 12, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                        .monospacedDigit()
                        .frame(maxWidth: 55)
                }
            } minimal: {
                Text(context.state.startTime, style: .timer)
                    .font(.system(size: 10, weight: .bold, design: .rounded))
                    .monospacedDigit()
            }
        }
    }
}
