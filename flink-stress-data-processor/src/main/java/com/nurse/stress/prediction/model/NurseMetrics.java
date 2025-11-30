package com.nurse.stress.prediction.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class NurseMetrics {
    private Integer id;
    private Float X;
    private Float Y;
    private Float Z;
    private Float EDA;
    private Float HR;
    private Float TEMP;
    private long datetime;
    private long windowStart;
    private long windowEnd;
}
