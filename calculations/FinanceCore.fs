module FinanceCore
open System

// Part 2: Fixed Income
let bondPrice faceValue couponRate marketRate years frequency =
    let periods = float years * float frequency
    let r = marketRate / float frequency
    let coupon = (faceValue * couponRate) / float frequency
    let pvCoupons = coupon * ((1.0 - (1.0 + r) ** -periods) / r)
    let pvFace = faceValue / ((1.0 + r) ** periods)
    pvCoupons + pvFace

// Part 3: Options (Black-Scholes)
let normalCDF x =
    let t = 1.0 / (1.0 + 0.2316419 * abs x)
    let d = 0.39894228 * exp (-x * x / 2.0)
    let p = d * t * (0.31938153 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    if x > 0.0 then 1.0 - p else p

let blackScholes S K T r sigma isCall =
    let d1 = (log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrt T)
    let d2 = d1 - sigma * sqrt T
    if isCall then S * normalCDF d1 - K * exp(-r * T) * normalCDF d2
    else K * exp(-r * T) * normalCDF (-d2) - S * normalCDF (-d1)

// Part 4: NPV
let npv rate (flows: float list) =
    flows |> List.mapi (fun i cf -> cf / ((1.0 + rate) ** float i)) |> List.sum

// Part 6: WACC
let wacc equity debt costEquity costDebt taxRate =
    let total = equity + debt
    let we = equity / total
    let wd = debt / total
    (we * costEquity) + (wd * costDebt * (1.0 - taxRate))

[<EntryPoint>]
let main argv =
    try
        match argv.[0] with
        | "bond" -> 
            printfn "%f" (bondPrice (float argv.[1]) (float argv.[2]) (float argv.[3]) (float argv.[4]) (float argv.[5]))
            0
        | "option" ->
            let isCall = (argv.[6].ToLower() = "call")
            printfn "%f" (blackScholes (float argv.[1]) (float argv.[2]) (float argv.[3]) (float argv.[4]) (float argv.[5]) isCall)
            0
        | "npv" ->
            let rate = float argv.[1]
            let flows = argv.[2].Split(',') |> Array.map float |> Array.toList
            printfn "%f" (npv rate flows)
            0
        | "wacc" ->
            printfn "%f" (wacc (float argv.[1]) (float argv.[2]) (float argv.[3]) (float argv.[4]) (float argv.[5]))
            0
        | _ -> 1
    with _ -> 1
