import ActivityKit
import SwiftUI
import TimerShared
import WidgetKit

struct WorkoutLiveActivityView: View {
    let context: ActivityViewContext<TimerActivityAttributes>

    var body: some View {
        HStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    Text("💪")
                        .font(.system(size: 14))
                    Text("NO ZERO DAY")
                        .font(.system(size: 10, weight: .black))
                        .foregroundColor(Color(red: 0.06, green: 0.73, blue: 0.60))
                        .kerning(1.5)
                }
                Text(context.state.startTime, style: .timer)
                    .font(.system(size: 36, weight: .black, design: .rounded))
                    .foregroundColor(.white)
                    .monospacedDigit()
                if !context.state.exerciseName.isEmpty {
                    Text(context.state.exerciseName)
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white.opacity(0.7))
                        .lineLimit(1)
                }
            }

            Spacer()

            if context.state.totalSets > 0 {
                VStack(spacing: 4) {
                    Text("\(context.state.currentSet)")
                        .font(.system(size: 32, weight: .black, design: .rounded))
                        .foregroundColor(Color(red: 0.06, green: 0.73, blue: 0.60))
                    Text("/ \(context.state.totalSets)세트")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.white.opacity(0.45))
                }
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 14)
        .activityBackgroundTint(Color(red: 0.02, green: 0.03, blue: 0.06))
    }
}

struct WorkoutLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: TimerActivityAttributes.self) { context in
            WorkoutLiveActivityView(context: context)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("💪 총 운동시간")
                            .font(.system(size: 10, weight: .medium))
                            .foregroundColor(.white.opacity(0.5))
                        Text(context.state.startTime, style: .timer)
                            .font(.system(size: 20, weight: .black, design: .rounded))
                            .foregroundColor(Color(red: 0.06, green: 0.73, blue: 0.60))
                            .monospacedDigit()
                    }
                }
                DynamicIslandExpandedRegion(.trailing) {
                    if context.state.totalSets > 0 {
                        VStack(alignment: .trailing, spacing: 2) {
                            Text("세트")
                                .font(.system(size: 10, weight: .medium))
                                .foregroundColor(.white.opacity(0.5))
                            Text("\(context.state.currentSet)/\(context.state.totalSets)")
                                .font(.system(size: 20, weight: .black, design: .rounded))
                                .foregroundColor(.white)
                        }
                    }
                }
                DynamicIslandExpandedRegion(.bottom) {
                    if !context.state.exerciseName.isEmpty {
                        Text(context.state.exerciseName)
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundColor(.white.opacity(0.8))
                    }
                }
            } compactLeading: {
                Text("💪").font(.caption2)
            } compactTrailing: {
                Text(context.state.startTime, style: .timer)
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundColor(Color(red: 0.06, green: 0.73, blue: 0.60))
                    .monospacedDigit()
                    .frame(maxWidth: 55)
            } minimal: {
                Text(context.state.startTime, style: .timer)
                    .font(.system(size: 10, weight: .bold, design: .rounded))
                    .monospacedDigit()
            }
        }
    }
}
