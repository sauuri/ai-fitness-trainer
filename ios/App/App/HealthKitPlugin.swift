import HealthKit
import Capacitor

@objc(HealthKitPlugin)
public class HealthKitPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "HealthKitPlugin"
    public let jsName = "HealthKitBridge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "requestAuth", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "getSteps", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "getSleepHours", returnType: CAPPluginReturnPromise),
    ]

    private let healthStore = HKHealthStore()

    @objc func getSleepHours(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable(),
              let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
            call.resolve(["hours": -1])
            return
        }
        // 어제 오후 6시 ~ 오늘 정오까지 (늦잠 포함)
        let now = Date()
        let noon = Calendar.current.date(bySettingHour: 12, minute: 0, second: 0, of: now) ?? now
        let yesterday6pm = Calendar.current.date(byAdding: .hour, value: -18, to: noon) ?? now
        let predicate = HKQuery.predicateForSamples(withStart: yesterday6pm, end: noon, options: .strictStartDate)
        let query = HKSampleQuery(sampleType: sleepType, predicate: predicate, limit: HKObjectQueryNoLimit, sortDescriptors: nil) { _, samples, _ in
            guard let samples = samples as? [HKCategorySample] else {
                call.resolve(["hours": -1]); return
            }
            let sleepValues: Set<Int> = [
                HKCategoryValueSleepAnalysis.asleepCore.rawValue,
                HKCategoryValueSleepAnalysis.asleepDeep.rawValue,
                HKCategoryValueSleepAnalysis.asleepREM.rawValue,
                HKCategoryValueSleepAnalysis.asleepUnspecified.rawValue,
            ]
            let totalSeconds = samples
                .filter { sleepValues.contains($0.value) }
                .reduce(0.0) { $0 + $1.endDate.timeIntervalSince($1.startDate) }
            let hours = (totalSeconds / 3600 * 2).rounded() / 2 // 0.5 단위 반올림
            call.resolve(["hours": hours > 0 ? hours : -1])
        }
        healthStore.execute(query)
    }

    @objc func requestAuth(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable() else {
            call.resolve(["granted": false, "reason": "not_available"])
            return
        }
        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount),
              let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
            call.resolve(["granted": false, "reason": "no_type"])
            return
        }
        healthStore.requestAuthorization(toShare: [], read: [stepType, sleepType]) { granted, error in
            if let err = error {
                call.resolve(["granted": false, "reason": err.localizedDescription])
            } else {
                call.resolve(["granted": granted])
            }
        }
    }

    @objc func getSteps(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable(),
              let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount) else {
            call.resolve(["steps": 0])
            return
        }
        let now = Date()
        let startOfDay = Calendar.current.startOfDay(for: now)
        let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: now, options: .strictStartDate)
        let query = HKStatisticsQuery(quantityType: stepType, quantitySamplePredicate: predicate, options: .cumulativeSum) { _, result, _ in
            let steps = result?.sumQuantity()?.doubleValue(for: HKUnit.count()) ?? 0
            call.resolve(["steps": Int(steps)])
        }
        healthStore.execute(query)
    }
}
