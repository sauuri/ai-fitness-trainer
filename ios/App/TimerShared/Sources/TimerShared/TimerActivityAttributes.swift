import ActivityKit
import Foundation

public struct TimerActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        public var startTime: Date
        public var elapsedSeconds: Int
        public var isPaused: Bool
        public var exerciseName: String
        public var currentSet: Int
        public var totalSets: Int

        public init(startTime: Date, elapsedSeconds: Int = 0, isPaused: Bool = false,
                    exerciseName: String = "", currentSet: Int = 0, totalSets: Int = 0) {
            self.startTime = startTime
            self.elapsedSeconds = elapsedSeconds
            self.isPaused = isPaused
            self.exerciseName = exerciseName
            self.currentSet = currentSet
            self.totalSets = totalSets
        }
    }

    public init() {}
}
