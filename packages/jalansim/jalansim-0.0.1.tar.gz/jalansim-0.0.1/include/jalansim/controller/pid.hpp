#pragma once

#include "jalansim/cuda_macros.hpp"

namespace jalansim::controller
{

    template <typename T>
    class PID
    {
    public:
        JALANSIM_HOST_DEVICE
        PID(T kp, T ki, T kd,
            T min_value = T(-1e9), T max_value = T(1e9),
            T min_output = T(-1e9), T max_output = T(1e9))
            : kp_(kp), ki_(ki), kd_(kd),
              prev_error_(T(0)), integral_(T(0)),
              min_value_(min_value), max_value_(max_value),
              min_output_(min_output), max_output_(max_output) {}

        JALANSIM_HOST_DEVICE
        T compute(T setpoint, T measured_value, T dt)
        {
            measured_value = clamp(measured_value, min_value_, max_value_);
            setpoint = clamp(setpoint, min_value_, max_value_);
            T error = setpoint - measured_value;
            integral_ += error * dt;
            T derivative = (error - prev_error_) / dt;
            T output = kp_ * error + ki_ * integral_ + kd_ * derivative;
            output = clamp(output, min_output_, max_output_);
            prev_error_ = error;
            return output;
        }

        JALANSIM_HOST_DEVICE
        void reset()
        {
            prev_error_ = T(0);
            integral_ = T(0);
        }

    private:
        JALANSIM_HOST_DEVICE
        static T clamp(T v, T lo, T hi)
        {
            return v < lo ? lo : (v > hi ? hi : v);
        }

        T kp_, ki_, kd_;
        T prev_error_, integral_;
        T min_value_, max_value_;
        T min_output_, max_output_;
    };

}