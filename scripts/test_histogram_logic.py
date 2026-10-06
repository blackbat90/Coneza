# Test script to verify SVG histogram generation logic
def generate_histogram_svg(capacity_kw=2200.0, mode="normal", has_bess=True, current_hour=14):
    w_total, h_total = 660, 215
    x_start = 45
    x_width = 600
    y_zero = 152
    h_pos_max = 130
    h_neg_max = 34
    
    max_pos = capacity_kw * 1.05
    max_neg = capacity_kw * 0.25 if has_bess else capacity_kw * 0.05
    
    col_w = x_width / 24  # 25px per hour
    bar_w = 17
    
    nap_points = []
    
    svg_elements = []
    
    import math
    for h in range(24):
        # Solar
        if 6 <= h <= 20:
            s_factor = math.sin((h - 6) / 14 * math.pi)
            if mode == "curtail" and 11 <= h <= 15:
                s_factor = min(s_factor, 0.5)
            pv_kw = capacity_kw * s_factor * 0.95
        else:
            pv_kw = 0.0
            
        # BESS
        bat_kw = 0.0
        if has_bess:
            if 10 <= h <= 14:
                bat_kw = -1 * min(capacity_kw * 0.16, 350.0) # charging
            elif (6 <= h <= 8) or (18 <= h <= 21):
                bat_kw = min(capacity_kw * 0.20, 480.0) # discharging
                if mode == "peak":
                    bat_kw *= 1.3
                    
        # Load
        load_kw = max(15.0, capacity_kw * 0.02)
        
        # Net NAP
        p_nap = max(0.0, pv_kw + bat_kw - load_kw)
        
        # Geometry
        x_bar = x_start + h * col_w + (col_w - bar_w) / 2
        
        # PV height
        h_pv = (pv_kw / max_pos) * h_pos_max
        y_pv = y_zero - h_pv
        
        # BESS discharge height (stacked on top of PV or separate)
        h_bat_dis = (max(0.0, bat_kw) / max_pos) * h_pos_max
        y_bat_dis = y_pv - h_bat_dis
        
        # BESS charge height (negative, down from y_zero)
        h_bat_chg = (abs(min(0.0, bat_kw)) / max_neg) * h_neg_max
        
        # Load height (negative, down from y_zero + h_bat_chg)
        h_load = (load_kw / max_neg) * h_neg_max
        
        # Net NAP Y
        y_nap = y_zero - (p_nap / max_pos) * h_pos_max
        x_center = x_start + h * col_w + col_w / 2
        nap_points.append(f"{x_center:.1f},{y_nap:.1f}")
        
    print(f"Generated {len(nap_points)} hourly points successfully. Current hour = {current_hour}")
    return True

generate_histogram_svg()
