import coins_dict
from app import Application
import database
import pandas as pd



if __name__ == "__main__":

    db = database.StockMarketDb()
    # db.init_local_db()
    # app = Application()
    # app.init_bybit()
    # app.init_bingx()

    # app.bybit_ex.import_stock_data_to_db(db)
    # app.bingx_ex.import_stock_data_to_db(db)

    # df = db.get_common_networks()
    #
    # res_df = pd.DataFrame()
    # for n in df['network_id'].unique():
    #
    #     ndf = df[df['network_id'] == n]
    #
    #     if len(ndf['stock_id'].unique()) > 1:
    #         ndf = ndf[ndf.duplicated('coin_id') | ndf.duplicated('coin_id', keep='last')]
    #         res_df = pd.concat([res_df, ndf])
    #
    #         pass

    # coin_list = db.get_common_coin_list()
    app = Application()
    app.init_bingx()
    app.init_bybit()
    # print(app.get_all_acc_balance())
    pass
    # app.bybit_ex.import_stock_data_to_db(db)
    app.track_coin(['EGLD'])
    # app.bybit_ex.place_order(0.5925, 2, 'ZRXUSDT', 'BUY')


