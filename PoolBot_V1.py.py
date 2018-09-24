#Or	iginally Written December 2017

#Setting API Keys
from binance.client import Client
client = Client("Public Key to be inserted here", "Secret Key to be inserted here")

import time

import math

from pymarketcap import Pymarketcap
cmc = Pymarketcap()

#Import of pymarketcap has issues upon startup at times, thus the repeated loop of trying to innitiate it is required until it succesfuly initiates

while True:
    try:
        binance = cmc.exchange('binance')
    except:
        pass
    else:
        break

#--------------------------------------
from binance.enums import *

#=======================================================
#Constant Variables
#-----------------
TRX_uptrgtfitprct = 20.0
TRX_lowtrgtfitprct = 19.75
IOTA_uptrgtfitprct = 17.0
IOTA_lowtrgtfitprct = 16.75
XRP_uptrgtfitprct = 15.0
XRP_lowtrgtfitprct = 14.50
BNB_uptrgtfitprct = 13.0
BNB_lowtrgtfitprct = 12.50
ADA_uptrgtfitprct = 11.0
ADA_lowtrgtfitprct = 10.50
LTC_uptrgtfitprct = 10.0
LTC_lowtrgtfitprct = 9.50
XLM_uptrgtfitprct = 9.0
XLM_lowtrgtfitprct = 8.00
SALT_uptrgtfitprct = 4.0
SALT_lowtrgtfitprct = 3.25
SUB_uptrgtfitprct = 4.0
SUB_lowtrgtfitprct = 3.25

#The above variables are the range within which we wish to trade each coin expressed as a percentage of our total assets
#======================================================

#Investment model
#if perctrx > uptargetperctrx
#		if candlestick condition to sell or hold
#if perctrx < lowtargetperctrx
#		if candlestick condition to buy or hold

#===================================================
#order = client.order_market_buy(
#    symbol='TickerBTC',
#    quantity=()

#order = client.order_market_sell(
#    symbol='TickerBTC',
#    quantity=()
#===================================================
#Master Code
#-----------

#ticker = 'TRX-BTC'
#ind = [x for x in range(len(binance)) if binance[x]['market'] == ticker][0]
#price = binance[ind]['price_usd']
#========================================
#Functions
#----------------------------------------
#Returns candlestick data from the web - this is used later to make buy/sell decisions
def colour(oursymbol):
    candles = client.get_klines(symbol = oursymbol, interval=KLINE_INTERVAL_30MINUTE)

    close = float(candles[-1][4])
    _open = float(candles[-1][1])

    return float(((close - _open)/_open)*100)

#===================================================
#Redistribute Function

#This function redistributes our assets amongst each coin such that we can stay within the inteded percentage range for each coin

def redistributeFunc(ourCoin):
    if ourCoin == 'TRX':
        trgtfitprct = TRX_uptrgtfitprct
        coinSymbol = 'TRXBTC'

    elif ourCoin == 'IOTA':
        trgtfitprct = IOTA_uptrgtfitprct
        coinSymbol = 'IOTABTC'

    elif ourCoin == 'XRP':
        trgtfitprct = XRP_lowtrgtfitprct
        coinSymbol = 'XRPBTC'

    elif ourCoin == 'BNB':
        trgtfitprct = BNB_lowtrgtfitprct
        coinSymbol = 'BNBBTC'

    elif ourCoin == 'ADA':
        trgtfitprct = ADA_lowtrgtfitprct
        coinSymbol = 'ADABTC'

    elif ourCoin == 'LTC':
        trgtfitprct = LTC_lowtrgtfitprct
        coinSymbol = 'LTCBTC'

    elif ourCoin == 'XLM':
        trgtfitprct = XLM_lowtrgtfitprct
        coinSymbol = 'XLMBTC'

    elif ourCoin == 'SALT':
        trgtfitprct = SALT_uptrgtfitprct
        coinSymbol = 'SALTBTC'

    elif ourCoin == 'SUB':
        trgtfitprct = SUB_uptrgtfitprct
        coinSymbol = 'SUBBTC'

    btcbalance = client.get_asset_balance(asset='BTC')
    qbtc = float(btcbalance['free'])

    redist = float((qbtc*0.5)*(trgtfitprct/100))

    stepSizefctr = client.get_symbol_info(coinSymbol)['filters'][1]['stepSize']
    lotSizefctr = int(round(math.log10(float(stepSizefctr)), 0))*int(-1)
    minQuant = float(client.get_symbol_info(coinSymbol)['filters'][1]['minQty'])
    maxQuant = float(client.get_symbol_info(coinSymbol)['filters'][1]['maxQty'])

    if minQuant < redist < maxQuant:
        client.order_market_buy(symbol = coinSymbol, quantity = round(redist, lotSizefctr))
        print('Redistributed BTC to ' + coinSymbol + ', bought ' + str(redist))
    else:
        print('Redistribution to ' + coinSymbol + 'did not meet conditions; tried to buy' + str(redist))


#=======================================================
#qrestoredown is quantity needed to rest to lowtrgtfitprct
#(lowtrgtfitprct/100)vAssets = newvalue_ticker
#newvalue_ticker/pticker = new quantity
#sell ticker at market with quantity(current asset balance - new quantity)


#qrestoreup is quantity needed to rest to uptrgtfitprct

def oursymbolDIR(our_symbol):
    return [x for x in range(len(client.get_all_tickers())) if client.get_all_tickers()[x]['symbol'] == our_symbol][0]

#Finds the dictionary within which the BNBBTC price is stored
#=======================================================
#Tether Function Code

#This is a failsafe function which converts the majority of our assets into USD_Teather when the entire market takes a downturn. It also buys back our traded coins when the market stabilizes again

def colourFunc(our_symbol):
    candles_coin = client.get_klines(symbol = our_symbol, interval=KLINE_INTERVAL_4HOUR)
    coin_close = float(candles_coin[-1][4])
    coin_open = float(candles_coin[-1][1])
    return float((coin_close - coin_open)*100/coin_open)

def colourPreFunc(our_symbol):
    candles_coin = client.get_klines(symbol = our_symbol, interval=KLINE_INTERVAL_4HOUR)
    coin_closepre = float(candles_coin[-2][4])
    coin_openpre = float(candles_coin[-2][1])
    return float((coin_closepre - coin_openpre)*100/coin_openpre)


def tetherFunc():
    avg_clr = (colourFunc('TRXBTC') + colourFunc('IOTABTC') + colourFunc('BNBBTC') + colourFunc('ADABTC') + colourFunc('LTCBTC') + colourFunc('XLMBTC') + colourFunc('SALTBTC') + colourFunc('SUBBTC'))/9
    print('AvgColour is ' + str(avg_clr))

    avgclrpre = (colourPreFunc('TRXBTC') + colourPreFunc('IOTABTC') + colourPreFunc('BNBBTC') + colourPreFunc('ADABTC') + colourPreFunc('LTCBTC') + colourPreFunc('XLMBTC') + colourPreFunc('SALTBTC') + colourPreFunc('SUBBTC'))/9
    print('Avg Pre Colour is ' + str(avgclrpre))

    btcbalance = client.get_asset_balance(asset='BTC')
    qbtc = float(btcbalance['free'])

    Qtether = float(((math.sqrt(math.fabs(avgclrpre)))/100)*qbtc)

    magprechange = math.fabs(avgclrpre)

    if magprechange > 100:
        q_mkt = qbtc
    elif magprechange < 100:
        q_mkt = Qtether

    stepSizefctr = client.get_symbol_info('BTCUSDT')['filters'][1]['stepSize']
    lotSizefctr = int(round(math.log10(float(stepSizefctr)), 0))*int(-1)
    minQuant = float(client.get_symbol_info('BTCUSDT')['filters'][1]['minQty'])
    maxQuant = float(client.get_symbol_info('BTCUSDT')['filters'][1]['maxQty'])

    magchange = math.fabs(avg_clr)

    if magchange >= 10:
        if avg_clr > 0 and minQuant < q_mkt < maxQuant:
            client.order_market_sell(symbol = 'BTCUSDT', quantity = round(q_mkt, lotSizefctr))
            print('Sold BTCUSDT')

        elif avg_clr < 0 and minQuant < q_mkt < maxQuant:
            client.order_market_buy(symbol = 'BTCUSDT', quantity = round(q_mkt, lotSizefctr))
            print('Bought BTCUSDT')
#=======================================================
def execution(coin):

#This function actually does the buying and selling of coins and adjusts how much to buy or sell depending on the worth of our total assets

    if coin == 'TRX':
        lowtrgtfitprct = TRX_lowtrgtfitprct
        uptrgtfitprct = TRX_uptrgtfitprct
        pcoin = ptrx
        qcoin = qtrx
        perccoin = perctrx
        oursymbol = 'TRXBTC'
        symbolDIR = trxDIR

    elif coin == 'IOTA':
        lowtrgtfitprct = IOTA_lowtrgtfitprct
        uptrgtfitprct = IOTA_uptrgtfitprct
        pcoin = piota
        qcoin = qiota
        perccoin = perciota
        oursymbol = 'IOTABTC'
        symbolDIR = iotaDIR

    elif coin == 'XRP':
        lowtrgtfitprct = XRP_lowtrgtfitprct
        uptrgtfitprct = XRP_uptrgtfitprct
        pcoin = pxrp
        qcoin = qxrp
        perccoin = percxrp
        oursymbol = 'XRPBTC'
        symbolDIR = xrpDIR

    elif coin == 'BNB':
        lowtrgtfitprct = BNB_lowtrgtfitprct
        uptrgtfitprct = BNB_uptrgtfitprct
        pcoin = pbnb
        qcoin = qbnb
        perccoin = percbnb
        oursymbol = 'BNBBTC'
        symbolDIR = bnbDIR

    elif coin == 'ADA':
        lowtrgtfitprct = ADA_lowtrgtfitprct
        uptrgtfitprct = ADA_uptrgtfitprct
        pcoin = pada
        qcoin = qada
        perccoin = percada
        oursymbol = 'ADABTC'
        symbolDIR = adaDIR

    elif coin == 'LTC':
        lowtrgtfitprct = LTC_lowtrgtfitprct
        uptrgtfitprct = LTC_uptrgtfitprct
        pcoin = pltc
        qcoin = qltc
        perccoin = percltc
        oursymbol = 'LTCBTC'
        symbolDIR = ltcDIR

    elif coin == 'XLM':
        lowtrgtfitprct = XLM_lowtrgtfitprct
        uptrgtfitprct = XLM_uptrgtfitprct
        pcoin = pxlm
        qcoin = qxlm
        perccoin = percxlm
        oursymbol = 'XLMBTC'
        symbolDIR = xlmDIR

    elif coin == 'SALT':
        lowtrgtfitprct = SALT_lowtrgtfitprct
        uptrgtfitprct = SALT_uptrgtfitprct
        pcoin = psalt
        qcoin = qsalt
        perccoin = percsalt
        oursymbol = 'SALTBTC'
        symbolDIR = saltDIR

    elif coin == 'SUB':
        lowtrgtfitprct = SUB_lowtrgtfitprct
        uptrgtfitprct = SUB_uptrgtfitprct
        pcoin = psub
        qcoin = qsub
        perccoin = percsub
        oursymbol = 'SUBBTC'
        symbolDIR = subDIR

    stepSizefctr = client.get_symbol_info(oursymbol)['filters'][1]['stepSize']
    lotSizefctr = int(round(math.log10(float(stepSizefctr)), 0))*int(-1)
    minQuant = float(client.get_symbol_info(oursymbol)['filters'][1]['minQty'])
    maxQuant = float(client.get_symbol_info(oursymbol)['filters'][1]['maxQty'])
    coinValBTC = float(client.get_all_tickers()[symbolDIR]['price'])
    btcbalance = client.get_asset_balance(asset='BTC')
    qbtc = float(btcbalance['free'])


    if perccoin > uptrgtfitprct:
        newvalue = (((float(lowtrgtfitprct))/100)*vAssets)
        newquantity = (float(newvalue))/(float(pcoin))
        qrestoredown = round(float(qcoin) - float(newquantity), lotSizefctr)

        if colour(oursymbol) < 0.0 and minQuant < qrestoredown < maxQuant and math.fabs(colour(oursymbol)) >= 1.11 and pcoin*qrestoredown >= 5.0:
            client.order_market_sell(symbol = oursymbol, quantity = qrestoredown)
            return 'sold ' + oursymbol + ', ' + str(qrestoredown)
        else:
            return 'restoredown is ' + str(qrestoredown)

    elif perccoin < lowtrgtfitprct:
        newvalue = (((float(uptrgtfitprct))/100)*vAssets)
        newquantity = (float(newvalue))/(float(pcoin))
        qrestoreup = round(float(newquantity) - float(qcoin), lotSizefctr)
        qValBTC = qrestoreup*coinValBTC

        if colour(oursymbol) > 0.0 and minQuant < qrestoreup < maxQuant and qValBTC <= qbtc and math.fabs(colour(oursymbol)) >= 1.11 and pcoin*qrestoreup >= 5.0:
            client.order_market_buy(symbol = oursymbol, quantity = qrestoreup)
            return 'bought ' + oursymbol + ', ' + str(qrestoreup)
        else:
            return 'restoreup is ' + str(qrestoreup)
#----------------------------------------------
#MAIN FUNCTION

#This is the main function and is actually what is running our bot 

while True:
    trxDIR = oursymbolDIR('TRXBTC')
    iotaDIR = oursymbolDIR('IOTABTC')
    xrpDIR = oursymbolDIR('XRPBTC')
    bnbDIR = oursymbolDIR('BNBBTC')
    adaDIR = oursymbolDIR('ADABTC')
    ltcDIR = oursymbolDIR('LTCBTC')
    xlmDIR = oursymbolDIR('XLMBTC')
    saltDIR = oursymbolDIR('SALTBTC')
    subDIR = oursymbolDIR('SUBBTC')

    count = 0
    t_end = time.time() + 60 * 60 * 24
    while time.time() < t_end:
        #---------------------------------------
        try:
            binance = cmc.exchange('binance')
              #test
            #btc
              #price

            pbtc = 15000

                #Quantity
            btcbalance = client.get_asset_balance(asset='BTC')
            qbtc = float(btcbalance['free'])

              #Total Value
            vbtc = pbtc*qbtc

            #trx
              #price
            trx = [x for x in range(len(binance)) if binance[x]['market'] == 'TRX-BTC'][0]
            ptrx = float(binance[trx]['price_usd'])

              #Quantity
            trxbalance = client.get_asset_balance(asset='TRX')
            qtrx = float(trxbalance['free'])

              #Total Value
            vtrx = ptrx*qtrx

            #iota
              #price
            iota = [x for x in range(len(binance)) if binance[x]['market'] == 'IOTA-BTC'][0]
            piota = float(binance[iota]['price_usd'])

              #Quantity
            iotabalance = client.get_asset_balance(asset='IOTA')
            qiota = float(iotabalance['free'])

              #Total Value
            viota = piota*qiota

            #xrp
              #price
            xrp = [x for x in range(len(binance)) if binance[x]['market'] == 'XRP-BTC'][0]
            pxrp = float(binance[xrp]['price_usd'])

              #Quantity
            xrpbalance = client.get_asset_balance(asset='XRP')
            qxrp = float(xrpbalance['free'])

              #Total Value
            vxrp = pxrp*qxrp

            #bnb
              #price
            bnb = [x for x in range(len(binance)) if binance[x]['market'] == 'BNB-BTC'][0]
            pbnb = float(binance[bnb]['price_usd'])

              #Quantity
            bnbbalance = client.get_asset_balance(asset='BNB')
            qbnb = float(bnbbalance['free'])

              #Total Value
            vbnb = pbnb*qbnb

            #ada
              #price
            ada = [x for x in range(len(binance)) if binance[x]['market'] == 'ADA-BTC'][0]
            pada = float(binance[ada]['price_usd'])

              #Quantity
            adabalance = client.get_asset_balance(asset='ADA')
            qada = float(adabalance['free'])

              #Total Value
            vada = pada*qada

            #ltc
              #price
            ltc = [x for x in range(len(binance)) if binance[x]['market'] == 'LTC-BTC'][0]
            pltc = float(binance[ltc]['price_usd'])

              #Quantity
            ltcbalance = client.get_asset_balance(asset='LTC')
            qltc = float(ltcbalance['free'])

              #Total Value
            vltc = pltc*qltc

            #xlm
              #price
            xlm = [x for x in range(len(binance)) if binance[x]['market'] == 'XLM-BTC'][0]
            pxlm = float(binance[xlm]['price_usd'])

              #Quantity
            xlmbalance = client.get_asset_balance(asset='XLM')
            qxlm = float(xlmbalance['free'])

              #Total Value
            vxlm = pxlm*qxlm

            #salt
              #price
            salt = [x for x in range(len(binance)) if binance[x]['market'] == 'SALT-BTC'][0]
            psalt = float(binance[salt]['price_usd'])

              #Quantity
            saltbalance = client.get_asset_balance(asset='SALT')
            qsalt = float(saltbalance['free'])

              #Total Value
            vsalt = psalt*qsalt

            #sub
              #price
            sub = [x for x in range(len(binance)) if binance[x]['market'] == 'SUB-BTC'][0]
            psub = float(binance[sub]['price_usd'])

              #Quantity
            subbalance = client.get_asset_balance(asset='SUB')
            qsub = float(subbalance['free'])

              #Total Value
            vsub = psub*qsub

            #-------------------------------------------------------
            #Total Assets
            vAssets = vtrx + viota + vxrp + vbnb + vada + vltc + vxlm + vsalt + vsub
            print(vAssets + vbtc)

            #percentages
            perctrx = vtrx/vAssets*100
            perciota = viota/vAssets*100
            percxrp = vxrp/vAssets*100
            percbnb = vbnb/vAssets*100
            percada = vada/vAssets*100
            percltc = vltc/vAssets*100
            percxlm = vxlm/vAssets*100
            percsalt = vsalt/vAssets*100
            percsub = vsub/vAssets*100
            #percbtc = vbtc/vAssets*100
            print(perctrx, perciota, percxrp, percbnb, percada, percltc, percxlm, percsalt, percsub)

            #-------------------------------------------------------


            #=======================================================

            #=======================================================
            #Bot Code
            tetherFunc()

            print(execution('TRX'))
            print(execution('IOTA'))
            print(execution('XRP'))
            print(execution('BNB'))
            print(execution('ADA'))
            print(execution('LTC'))
            print(execution('XLM'))
            print(execution('SALT'))
            print(execution('SUB'))
        except:
            pass
        else:
            pass
        print(count)
        count += 1
    redistributeFunc('TRX')
    redistributeFunc('IOTA')
    redistributeFunc('XRP')
    redistributeFunc('BNB')
    redistributeFunc('ADA')
    redistributeFunc('LTC')
    redistributeFunc('XLM')
    redistributeFunc('SALT')
    redistributeFunc('SUB')
