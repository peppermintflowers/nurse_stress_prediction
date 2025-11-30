package com.nurse.stress.prediction.processing;

import com.nurse.stress.prediction.SensorRecord;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.java.tuple.Tuple7;

public class AverageAggregator implements AggregateFunction<SensorRecord, Tuple7<Double, Double, Double, Double, Double, Double, Long>,
        Tuple7<Double, Double, Double, Double, Double, Double, Long>> {

    @Override
    public Tuple7<Double, Double, Double, Double, Double, Double, Long> createAccumulator() {
        return Tuple7.of(0.0,0.0,0.0,0.0,0.0,0.0,0L);
    }

    @Override
    public Tuple7<Double, Double, Double, Double, Double, Double, Long> add(SensorRecord record, Tuple7<Double, Double, Double, Double, Double, Double, Long> acc) {
        double x = record.getX() == null ? 0f : record.getX();
        double y = record.getY() == null ? 0f : record.getY();
        double z = record.getZ() == null ? 0f : record.getZ();
        double eda = record.getEDA() == null ? 0f : record.getEDA();
        double hr = record.getHR() == null ? 0f : record.getHR();
        double temp = record.getTEMP() == null ? 0f : record.getTEMP();

        return Tuple7.of(
                acc.f0 + x,
                acc.f1 + y,
                acc.f2 + z,
                acc.f3 + eda,
                acc.f4 + hr,
                acc.f5 + temp,
                acc.f6 + 1
        );
    }

    @Override
    public Tuple7<Double, Double, Double, Double, Double, Double, Long> merge(Tuple7<Double, Double, Double, Double, Double, Double, Long> a, Tuple7<Double, Double, Double, Double, Double, Double, Long> b) {
        return Tuple7.of(
                a.f0 + b.f0,
                a.f1 + b.f1,
                a.f2 + b.f2,
                a.f3 + b.f3,
                a.f4 + b.f4,
                a.f5 + b.f5,
                a.f6 + b.f6
        );
    }


    @Override
    public Tuple7<Double, Double, Double, Double, Double, Double, Long> getResult(Tuple7<Double, Double, Double, Double, Double, Double, Long> acc) {
        return acc;
    }
}
