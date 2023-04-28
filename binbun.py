import config, logging, time
from flask import request, url_for, redirect, flash, Blueprint, render_template
from binance.um_futures import UMFutures
from binance.error import ClientError

#print("Syncing time")
#os.system('w32tm/resync') #Needs admin rights
#print(os)

baseurl = "https://fapi.binance.com"
#baseurl = "https://testnet.binancefuture.com"
client = UMFutures(key=config.API_KEY, secret=config.API_SECRET, base_url=baseurl)

risklevel = 3.0 #RiskLevel
ticker = "BTCBUSD"
roundvar = 1 #For rounding Price example 24609.3
roundunits = 3 #For rounding order size like 0.001
openorderstr = "0.000" #Zero order string for BTCBUSD

routes = Blueprint('routes', __name__, static_folder='static', template_folder='templates')

@routes.route('/getbalancetest')
def getbalance():
    try:
        result = client.balance(recvWindow=6000)
        response = ""
        for i in result:
            if i["asset"] == "BUSD":
                response = i["balance"]
        logging.info(response)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return False
    return response

def getSizeDynamic(side, entry, sl):
    try:
        print(f"Get size with RiskLevel {risklevel} for BTCBUSD")      
        
        balance = getbalance()
        pnl = float(balance) / 100.0 * risklevel
        
        if side == "BUY":
            sl_percent = (entry - sl)/entry
        elif side == "SELL":
            sl_percent = (sl - entry)/entry

        size_cash = pnl / (sl_percent*100.0) * 100.0
        size = 1.0 / entry * size_cash
        size_round = round(size,roundunits)
        print(f"Dynamic size for {side} |Balance {balance} |Entry {entry} |SL {sl} |Cash {size_cash} |Qty {size_round}")
    except Exception as e:
        print("an exception occured - {}".format(e))
        return {
            "code": "error",
            "message": "Size calculation failed"
        }
    return size_round

def getLimitPrice(side, entry, sl, riskreward):
    try:
        print(f"Get Limit price with |Entry {entry} |SL {sl} |RiskReward {riskreward}:")
        if side == "BUY":
            limitprice = entry+((entry - sl)*riskreward)
        elif side == "SELL":
            limitprice = entry-((sl - entry)*riskreward)
        price = round(limitprice,roundvar)
        print(f"Limit price: {price}")
    except Exception as e:
        print("an exception occured - {}".format(e))
        return {
            "code": "error",
            "message": "Limit Price calculation failed"
        }
    return price

@routes.route('/postmarketorder', methods=['POST'])
def postmarketorder():
    print("Postmarketorder route:")
    riskreward = float(request.form['riskreward'])
    stoploss = request.form['stoploss']
    ordertype = request.form['ordertype']
    
    price = float(client.mark_price(ticker)["markPrice"])
    slprice = round(float(stoploss),roundvar)
    qty = getSizeDynamic(ordertype, price, slprice)
    
    # Post a new order
    params = {
        'symbol': ticker,
        'side': ordertype,
        'type': 'MARKET',
        'quantity': qty,
        }
    order = client.new_order(**params)
    print(f"Send Market Order: ", order)
    
    if order:
        side = "SELL"
        if ordertype == "SELL":
            side = "BUY"
        params = {
        'symbol': ticker,
        'side': side,
        'type': 'STOP_MARKET',
        'quantity': qty,
        'stopPrice': slprice,
        'reduceOnly': 'true'
        }
        slorder = client.new_order(**params)
        print(f"Send StopLoss Order: ",slorder)
        if slorder:
            limittpprice = getLimitPrice(side, price, slprice, riskreward)
            params = {
                'symbol': ticker,
                'side': side,
                'type': 'TAKE_PROFIT_MARKET',
                'quantity': qty,
                'stopPrice': limittpprice,
                'reduceOnly': 'true',
                'timeInForce': 'GTC'}
            limittporder = client.new_order(**params)
            #limittporder = takeprofitorder(side,qty,ticker,limittpprice,)
            print(f"Send Limit Order: ",limittporder)
        flash(f'Submitted Market order! {ticker} |RR {riskreward} |SL {stoploss}', 'cancelallorders')
    else:
        flash('Error on postmarketorder! Check code!', 'cancelallorders')
    return redirect(url_for('routes.tradeov'))

def transhistorycalculated(inputdata):
    data = inputdata
    #print(data)
    result = 0.0
    for x in data:
        result = result + float(x["income"])
    return round(result,3)

def current_milli_time():
    return round(time.time() * 1000)

@routes.route('/tradeov')
def tradeov():
    print("Tradeov route:")
    ##Current milliseconds minus 3 months## old 1674153036675
    startmilli = current_milli_time() - 7889238000
    if startmilli < 1677735866163:
        startmilli = 1677735866163
    ##END##
    markprice = round(float(client.mark_price("BTCBUSD")["markPrice"]),1)
    balance = round(float(getbalance()),3)
    type = "REALIZED_PNL"
    pasthist_btc = client.get_income_history(symbol=ticker,incomeType=type,startTime=startmilli,limit=1000)
    histbtc = transhistorycalculated(pasthist_btc)
    openpositionbtc = client.get_position_risk(symbol=ticker)[0]["positionAmt"]
    openorders = client.get_orders(symbol=ticker)
    openposition = client.get_position_risk(symbol=ticker)
    return render_template('tradeov.html', risklevel=risklevel, openorders=openorders, openposition=openposition, pasthist_btc=pasthist_btc, histbtc=histbtc, markprice=markprice, balance=balance, openpositionbtc=openpositionbtc)

def closeslorder(side, quantity, symbol, sl, order_type="STOP_MARKET"):
    try:
        print(f"Sending fast CloseSLorder |Type {order_type} |Side {side} |Qty {quantity} |Price {sl}")
        trailslorder = client.new_order(symbol=symbol, side=side, type=order_type, quantity=quantity, stopPrice=sl, reduceOnly="true")
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return False
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return trailslorder

@routes.route('/closestop', methods=['POST'])
def closestop():
    print("Closestop route:")
    data = request.form
    markprice = round(float(client.mark_price("BTCBUSD")["markPrice"]),roundvar)
    price = markprice - 0.5
    sl = round(price,2)
    positionamt = data['positionAmt']
    qty = float(positionamt)
    side = "SELL"
    if qty < 0:
        qty = qty * (-1)
        side = "BUY"
        price = markprice + 0.5
        sl = round(price,2)
    taketp = closeslorder(side,qty,ticker,sl)
    print(f"Stop Order TakeProfit {taketp}")
    if taketp:
        flash('Stop Order Position set!', 'cancelallorders')
        return redirect(url_for('routes.tradeov'))
    else:
        flash('Error! Check Code!', 'cancelallorders')
        print("Error while trying to set stopclose!")
        return redirect(url_for('routes.tradeov'))

def tporder(side, qty, order_type="MARKET"):
    try:
        print(f"Sending TakeProfit |Type {order_type} |Side {side} |Qty {qty}")
        tporder = client.new_order(symbol=ticker, side=side, type=order_type, quantity=qty, reduceOnly="true")
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return False
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return tporder

@routes.route('/closehook', methods=['POST'])
def closehook():
    print("Closehook route:")
    data = request.form
    positionamt = data['positionAmt']
    qty = float(positionamt)
    side = "SELL"
    if qty < 0:
        qty = qty * (-1)
        side = "BUY"
    taketp = tporder(side, qty)
    print(f"Manual TakeProfit {taketp}")
    if taketp:
        flash('Position closed!', 'cancelallorders')
        return redirect(url_for('routes.tradeov'))
    else:
        flash('Error! Check Code!', 'cancelallorders')
        print("Error while trying to manual close a position!")
        return redirect(url_for('routes.tradeov'))
    
@routes.route('/closeorderid', methods=['POST'])
def closeorderid():
    print("Closeorderid route:")
    orderid = request.form['orderid']
    response = client.cancel_order(symbol=ticker, orderId=orderid)
    if response:
        flash(f'OrderId {orderid} canceled!', 'cancelallorders')
    else:
        flash('Error! Check Code!', 'cancelallorders')
    return redirect(url_for('routes.tradeov'))

def check_slOrder_dublicate(symbol, stopprice, roundingvar):
    openorders = client.get_orders(symbol=symbol)
    dublicate = False
    for data in openorders:
        orderprice = round(float(data['stopPrice']),roundingvar)
        if data['type'] == "STOP_MARKET" and orderprice == stopprice:
            print(f"Found SL Order duplicate {symbol} at {stopprice}")
            dublicate = True
        else:
            print(f"New SL Order is unique: {symbol} at {stopprice}")
    return dublicate

def trailslorder(side, quantity, sl, order_type="STOP_MARKET"):
    try:
        print(f"Sending TrailSLorder |Type {order_type} |Side {side} |Qty {quantity} |Price {sl}")
        trailslorder = client.new_order(symbol=ticker, side=side, type=order_type, quantity=quantity, stopPrice=sl, reduceOnly="true")
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return False
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return trailslorder

@routes.route('/stoptrail', methods=['POST'])
def stoptrail():
    print(f"Stoptrail route:")
    openposition = client.get_position_risk(symbol=ticker)[0]["positionAmt"]
    slorder_response = False
    price = request.form['orderprice']
    if openposition != openorderstr:
        orderprice = round(float(price),roundvar)
        orderaction = request.form['orderaction']
        if check_slOrder_dublicate(ticker, orderprice, roundvar) == False:
            quantityor = float(openposition)
            if quantityor < 0:
                quantityor = quantityor * (-1)
            slorder_response = trailslorder(orderaction, quantityor, orderprice)
            print(f"Position {quantityor} still open - {orderprice} send Trail SL order")
            print(slorder_response)
            flash(f'Submitted Stop Trail! {ticker} |SL {price} |Side {orderaction} |Qty {quantityor}', 'cancelallorders')
    else:
        print(f"{ticker} has no open position")
        flash('Error on postmarketorder! Check code!', 'cancelallorders')
    return redirect(url_for('routes.tradeov'))

def cancelallopenorders(symbol):
    try:
        cancel = client.cancel_open_orders(symbol)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return False
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return cancel

@routes.route('/cancelallorders', methods=['POST'])
def cancelallorders():
    print(f"Cancelallorders route:")
    closesl = False
    openposition = client.get_position_risk(symbol=ticker)[0]["positionAmt"]
    if openposition == openorderstr:
        closesl = cancelallopenorders(ticker)
        print(closesl)
        flash('Cancelallorders', 'cancelallorders')
    else:
        print(f"{ticker} has an open position of {openposition}")
    return redirect(url_for('routes.tradeov'))

def limitorder(side, quantity, symbol, limitprice, order_type="LIMIT"):
    try:
        print(f"Sending LimitEntry |Type {order_type} |Side {side} |Qty {quantity} |Limitprice {limitprice}")
        limittporder = client.new_order(symbol=symbol, side=side, type=order_type, quantity=quantity, price=limitprice, timeInForce="GTC")
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return False
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return limittporder

def takeprofitorder(side, quantity, symbol, tpprice, order_type='TAKE_PROFIT_MARKET'):
    try:
        print(f"Sending TakeProfit stop order {order_type} - {side} {quantity} {symbol} - Price {tpprice}")
        takeprofitorder = client.new_order(symbol=symbol, side=side, type=order_type, quantity=quantity, stopPrice=tpprice, reduceOnly="true")
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return False
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return takeprofitorder

@routes.route('/postlimitorder', methods=['POST'])
def postlimitorder():
    print("Postlimitorder route:")
    entry = round(float(request.form['orderprice']),roundvar)
    sl = round(float(request.form['stoploss']),roundvar)
    riskreward = float(request.form['riskreward'])
    orderaction = request.form['orderaction']
    tp = getLimitPrice(orderaction, entry, sl, riskreward)
    quantity = getSizeDynamic(orderaction, entry, sl)
    order = limitorder(orderaction, quantity, ticker, entry)
    print(order)
    if order:
        side = "SELL"
        if orderaction == "SELL":
            side = "BUY"
        params = {
        'symbol': ticker,
        'side': side,
        'type': 'STOP_MARKET',
        'quantity': quantity,
        'stopPrice': sl,
        'reduceOnly': 'true'
        }
        slorder = client.new_order(**params)
        print(slorder)
        if slorder:
            tporder = takeprofitorder(side, quantity, ticker, tp)
            print(tporder)
        flash(f'Submitted Limit Entry! {ticker} |Price {entry} |Side {orderaction} |SL {sl} |Qty {quantity}', 'cancelallorders')
    else:
        flash('Error on postlimitorder! Check code!', 'cancelallorders')
    return redirect(url_for('routes.tradeov'))