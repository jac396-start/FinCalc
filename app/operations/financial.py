import subprocess
import os
import shutil

# Path configured in Dockerfile
FSHARP_EXEC = os.getenv("FSHARP_EXEC_PATH", "./calculations/bin/Release/net6.0/FinanceCore")

def run_fsharp_cmd(args: list) -> float:
    # Check if we should use dotnet run (local dev) or exec (docker)
    cmd = []
    if not os.path.exists(FSHARP_EXEC) and shutil.which("dotnet"):
         cmd = ["dotnet", "run", "--project", "./calculations/FinanceCore.fsproj", "--"] + args
    else:
        cmd = [FSHARP_EXEC] + args

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Engine Error: {e}")
        return 0.0

def calculate_bond(face, coupon, market, years, freq=2):
    return run_fsharp_cmd(["bond", str(face), str(coupon), str(market), str(years), str(freq)])

def calculate_wacc(equity, debt, cost_e, cost_d, tax):
    return run_fsharp_cmd(["wacc", str(equity), str(debt), str(cost_e), str(cost_d), str(tax)])

def calculate_option(spot, strike, time, rate, vol, kind):
    return run_fsharp_cmd(["option", str(spot), str(strike), str(time), str(rate), str(vol), kind])

def calculate_npv(rate, flows):
    flow_str = ",".join(map(str, flows))
    return run_fsharp_cmd(["npv", str(rate), flow_str])
