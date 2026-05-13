import numpy as np

def simulate_nickel(market_type, reserve, r, demand_slope, n_firms=3):
    years = 20
    prices = []
    extraction = []
    remaining_reserve = reserve
    
    # Simple Hotelling-style simulation
    p0 = 15000 # Harga awal asumsi
    
    for t in range(years):
        if market_type == "Persaingan Sempurna":
            p_t = p0 * (1 + r)**t
        elif market_type == "Monopoli":
            # Monopoli menaikkan harga lebih lambat tapi mulai dari titik lebih tinggi
            p_t = (p0 * 1.5) * (1 + (r/2))**t
        else: # Oligopoli
            p_t = (p0 * 1.2) * (1 + (r/1.5))**t
            
        # Hitung ekstraksi berdasarkan fungsi permintaan sederhana Q = a - bP
        q_t = max(0, 1000 - (demand_slope * (p_t / 1000)))
        
        if remaining_reserve <= 0:
            q_t = 0
            
        remaining_reserve -= q_t
        prices.append(p_t)
        extraction.append(q_t)
        
    return prices, extraction
