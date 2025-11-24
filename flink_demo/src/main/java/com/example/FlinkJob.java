package com.example;

import org.apache.flink.api.common.functions.RichMapFunction;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.functions.source.SourceFunction;

import java.util.Random;

public class FlinkJob {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        DataStream<long[]> numbers = env.addSource(new SourceFunction<long[]>() {
            private volatile boolean running = true;
            private Random random = new Random();

            @Override
            public void run(SourceContext<long[]> ctx) throws Exception {
                while (running) {
                    long a = random.nextInt(100);
                    long b = random.nextInt(100);
                    long c = random.nextInt(100);
                    ctx.collect(new long[]{a, b, c});
                    Thread.sleep(500);
                }
            }

            @Override
            public void cancel() {
                running = false;
            }
        });

        DataStream<IOTPing> events=numbers.map(new RichMapFunction<long[], IOTPing>() {
            //private transient Gauge<Long> valueGauge;
            //private transient Gauge<Long> multipliedGauge;

            /*@Override
            public void open(Configuration parameters) {
                // Register gauges to Flink metrics
                valueGauge = getRuntimeContext()
                        .getMetricGroup()
                        .gauge("value_original", () -> currentValue);
                multipliedGauge = getRuntimeContext()
                        .getMetricGroup()
                        .gauge("value_multiplied", () -> currentMultiplied);
            }*/

            @Override
            public IOTPing map(long[] value) {
                long id = value[0];
                long feature = value[1];
                long multiplied = value[1] * 2;

                System.out.printf(
                        "Id: %d, Feature: %d, Multiplied: %d%n",
                        id, feature, multiplied
                );

                return new IOTPing(id, feature, multiplied);
            }

        });
        events.addSink(new InfluxSinkPing());
        env.execute("Flink Streaming Metrics Example");
    }
}

