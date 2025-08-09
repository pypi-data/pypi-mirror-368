#pragma once
#include <jalansim/cuda_macros.hpp>
#include <cmath>

namespace jalansim::dynamics::models {

struct BicycleDrift
{
    static constexpr std::size_t STATE_DIM = 9;
    static constexpr std::size_t INPUT_DIM = 2;

    
    double a  = 1.1;
    double b  = 1.6;
    double h  = 0.5;
    double m  = 1300.0;
    double I_z = 2000.0;
    double I_y_w = 1.2;
    double R_w   = 0.33;

    
    double C_alpha = 80000.0;

    
    double delta_min      = -0.6;
    double delta_max      =  0.6;
    double delta_dot_min  = -1.0;
    double delta_dot_max  =  1.0;

    
    double acc_min   = -5.0;
    double acc_max   =  3.0;

    
    double v_switch  = 0.2;
    double v_blend   = 0.05;

    
    double T_sb = 0.5;
    double T_se = 0.5;

    
    JALANSIM_HOST_DEVICE
    static double clamp(double v,double lo,double hi)
        { return v<lo?lo:(v>hi?hi:v); }

    
    JALANSIM_HOST_DEVICE
    double steering_limit(double delta, double delta_dot_cmd, double dt) const
    {
        double d_dot = clamp(delta_dot_cmd, delta_dot_min, delta_dot_max);
        if (dt > 0.0) {
            double next = delta + d_dot*dt;
            if (next > delta_max) d_dot = (delta_max-delta)/dt;
            if (next < delta_min) d_dot = (delta_min-delta)/dt;
        }
        return d_dot;
    }

    
    JALANSIM_HOST_DEVICE
    double accel_limit(double a_cmd) const
    {
        return clamp(a_cmd, acc_min, acc_max);
    }

    
    JALANSIM_HOST_DEVICE
    double Fy_linear(double alpha, double F_z) const
    { return -C_alpha * alpha; }       

    JALANSIM_HOST_DEVICE
    double Fx_simple(double slip, double F_z) const
    { return -C_alpha * slip; }        

    
    JALANSIM_HOST_DEVICE
    void rhs_kin_cog(const double* x, const double* u,
                     double* dx) const
    {
        double lwb = a + b;
        double delta = x[2];
        double v     = x[3];
        double psi   = x[4];
        dx[0] = v * std::cos(psi);
        dx[1] = v * std::sin(psi);
        dx[2] = u[0];
        dx[3] = u[1];
        dx[4] = v / lwb * std::tan(delta);
    }

    
    JALANSIM_HOST_DEVICE
    void rhs(const double* x, const double* u_cmd,
             double* dx, double dt) const
    {
        
        const double X        = x[0];
        const double Y        = x[1];
        const double delta    = x[2];
        const double v        = x[3];
        const double psi      = x[4];
        const double psi_dot  = x[5];
        const double beta     = x[6];
        const double omega_f  = x[7];
        const double omega_r  = x[8];

        
        double delta_dot = steering_limit(delta, u_cmd[0], dt);
        double a_long    = accel_limit(u_cmd[1]);

        
        double alpha_f = 0.0, alpha_r = 0.0;
        if (std::abs(v) > 1e-3) {
            alpha_f = std::atan((v*std::sin(beta) + psi_dot*a) /
                                (v*std::cos(beta))) - delta;
            alpha_r = std::atan((v*std::sin(beta) - psi_dot*b) /
                                (v*std::cos(beta)));
        }

        
        double F_zf = m * (-a_long * h + g * b) / (a + b);
        double F_zr = m * ( a_long * h + g * a) / (a + b);

        
        double u_wf = v*std::cos(beta)*std::cos(delta) +
                      (v*std::sin(beta) + psi_dot*a) * std::sin(delta);
        double u_wr = v*std::cos(beta);

        
        const double v_min = 0.01;
        double slip_f = 1.0 - R_w * omega_f / (u_wf > v_min ? u_wf : v_min);
        double slip_r = 1.0 - R_w * omega_r / (u_wr > v_min ? u_wr : v_min);

        
        double Fx_f = Fx_simple(slip_f, F_zf);
        double Fx_r = Fx_simple(slip_r, F_zr);
        double Fy_f = Fy_linear(alpha_f, F_zf);
        double Fy_r = Fy_linear(alpha_r, F_zr);

        
        double T_B = a_long > 0 ? 0.0 : m * R_w * a_long;
        double T_E = a_long > 0 ? m * R_w * a_long : 0.0;

        
        double domega_f = (1.0 / I_y_w) *
                          (-R_w * Fx_f + T_sb * T_B + T_se * T_E);
        double domega_r = (1.0 / I_y_w) *
                          (-R_w * Fx_r + (1 - T_sb)*T_B + (1 - T_se)*T_E);
        if (omega_f <= 0.0 && domega_f < 0.0) domega_f = 0.0;
        if (omega_r <= 0.0 && domega_r < 0.0) domega_r = 0.0;

        
        double dv      = ( -Fy_f*std::sin(delta-beta)
                           + Fy_r*std::sin(beta)
                           + Fx_r*std::cos(beta)
                           + Fx_f*std::cos(delta-beta) ) / m;

        double psi_dd  = (Fy_f*std::cos(delta)*a - Fy_r*b
                          + Fx_f*std::sin(delta)*a) / I_z;

        double beta_d  = std::abs(v)>1e-3 ?
            (-psi_dot + (Fy_f*std::cos(delta-beta)+Fy_r*std::cos(beta)
                        -Fx_r*std::sin(beta)+Fx_f*std::sin(delta-beta)) / (m*v))
            : 0.0;

        
        double f_ks[5];
        rhs_kin_cog(x, (double[]){delta_dot, a_long}, f_ks);
        double beta_d_ks = (b*delta_dot) /
            ((a+b)*std::cos(delta)*std::cos(delta)) /
            (1.0 + std::pow(std::tan(delta)*b/(a+b),2));

        double psi_dd_ks = 1.0/(a+b) *
           (a_long*std::cos(beta)*std::tan(delta)
            - v*std::sin(beta)*beta_d_ks*std::tan(delta)
            + v*std::cos(beta)*delta_dot/std::cos(delta)/std::cos(delta));

        
        double w_dyn = 0.5 * (std::tanh((v - v_switch)/v_blend) + 1.0);
        double w_ks  = 1.0 - w_dyn;

        
        dx[0] = v * std::cos(beta + psi);               
        dx[1] = v * std::sin(beta + psi);               
        dx[2] = delta_dot;
        dx[3] = w_dyn*dv      + w_ks*f_ks[3];
        dx[4] = w_dyn*psi_dot + w_ks*f_ks[4];
        dx[5] = w_dyn*psi_dd  + w_ks*psi_dd_ks;
        dx[6] = w_dyn*beta_d  + w_ks*beta_d_ks;
        dx[7] = w_dyn*domega_f + w_ks*( (u_wf/R_w - omega_f)/0.02 );
        dx[8] = w_dyn*domega_r + w_ks*( (u_wr/R_w - omega_r)/0.02 );
    }

    JALANSIM_HOST_DEVICE
    void reset() {}
};

}
