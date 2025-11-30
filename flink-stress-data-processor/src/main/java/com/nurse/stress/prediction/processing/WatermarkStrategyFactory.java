package com.nurse.stress.prediction.processing;

import com.nurse.stress.prediction.SensorRecord;
import org.apache.flink.api.common.eventtime.SerializableTimestampAssigner;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;

public class WatermarkStrategyFactory {

    private static final DateTimeFormatter FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSSSSS");

    public static WatermarkStrategy<SensorRecord> create() {
        return WatermarkStrategy
                .<SensorRecord>forBoundedOutOfOrderness(Duration.ofSeconds(5))
                .withTimestampAssigner(new SerializableTimestampAssigner<SensorRecord>() {
                    @Override
                    public long extractTimestamp(SensorRecord element, long recordTimestamp) {
                        return parseTimestamp(element.getDatetime());
                    }
                });
    }

    private static long parseTimestamp(String ts) {
        if (ts == null) return System.currentTimeMillis();

        LocalDateTime ldt = LocalDateTime.parse(ts, WatermarkStrategyFactory.FORMATTER);

        return ldt.toInstant(ZoneOffset.UTC).toEpochMilli();
    }
}
