#show results passing a list of trades
def show_multiassets_results(df_result, number_of_assets, **kwargs):
    final_df = df_result.sort_values(by=['ExitTime'])
    final_df.set_index('ExitTime', inplace = True)
    starting_balance = 100000
    final_equity = starting_balance
    max_equity = starting_balance
    max_drawdown = 0
    win_counter = 0
    avg_trade_sum = 0
    avg_win_trade_sum = 0
    avg_loss_trade_sum = 0

    for index, row in final_df.iterrows():
        avg_trade_sum = avg_trade_sum + row['ReturnPct']

        final_equity = final_equity + (final_equity/100*row['ReturnPct']) 
        drawdown = - (max_equity - final_equity) / max_equity * 100

        if drawdown < max_drawdown:
            max_drawdown = drawdown

        if final_equity > max_equity:
            max_equity = final_equity

        if row['ReturnPct'] > 0:
            win_counter = win_counter + 1
            avg_win_trade_sum = avg_win_trade_sum + row['ReturnPct']
        else:
            avg_loss_trade_sum = avg_loss_trade_sum + row['ReturnPct']

    return (
        "--- Results MultiAssets w/ params: fast_ema {fast_ema_period}, slow_ema: {slow_ema_period} --- \n"
            "# Assets: {number_of_assets} \n"
            "# Trades: {trades} \n"
            "Equity Start [$]: {starting_balance} \n"
            "Equity Final [$] : {equity_final_dollar} \n"
            "Return [%]: {return_percentage} \n"
            "Max. Drawdown [%]: {max_drawdown_percentage} \n"
            "Win Rate [%]: {win_rate_percentage} \n"
            "Avg Win when win [%]: {avg_win_percentage} \n"
            "Avg Loss when loss [%]: {avg_loss_percentage} \n"
            "Avg Trade [%]: {avg_trade_percentage} \n"
        .format(
            number_of_assets = number_of_assets,
            trades = str(len(final_df.index)),
            starting_balance = starting_balance,
            equity_final_dollar = str(round(final_equity, 2)),
            return_percentage =  str(round((final_equity - starting_balance) / starting_balance * 100, 2)),
            max_drawdown_percentage = str(round(max_drawdown, 2)),
            win_rate_percentage = str(round( win_counter / len(final_df.index) * 100, 2)),
            avg_win_percentage = str(round( avg_win_trade_sum / win_counter, 2)),
            avg_loss_percentage = str(round( avg_loss_trade_sum / (len(final_df.index) - win_counter), 2)),
            avg_trade_percentage = str(round( avg_trade_sum / len(final_df.index), 2)),
            fast_ema_period =  kwargs.get("fast_ema_period"),
            slow_ema_period =  kwargs.get("slow_ema_period")
        )
    )