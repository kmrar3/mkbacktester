class signalHandler:

    def __init__(self,stop_loss,take_profit,broker_cost,data):
        # Parameters initialised
        self.original_stop_loss = stop_loss
        self.original_take_profit = take_profit
        self.broker_cost = broker_cost
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.prev_traded_position = 0
        self.prev_traded_price = None

        self.total_profit = 0
        data['action'] = ''
        data['P/L'] = ''
        data['Total profit'] = ''
        n = len(data)
        self.action = [""]*n
        self.arr_PL = [""]*n 
        self.arr_total_profit = [""]*n 
        self.current_action = ""
        self.data = data        

    ############### Helpers ###############

    def bandPL(self,PL):
        # Floors or ceils PL
        # Check for take profit and stop loss value and return PL
        if PL > self.take_profit:
            PL = self.take_profit
        elif PL < self.stop_loss:
            PL = self.stop_loss
        return PL

    
    def closeTrade(self,PL):
        # Only called when a trade happens
        # Reseting Current position,action AND toal profit
        # Set the current action based on previous traded position
        # Calculate total profit
        if self.prev_traded_position == -1:
            self.current_action = "short_buy"
        elif self.prev_traded_position == 1:
            self.current_action = "sell"        
        
        self.total_profit += PL

        self.prev_traded_position = 0
        self.prev_traded_price = None

        self.stop_loss = self.original_stop_loss
        self.take_profit = self.original_take_profit
        
    def saveStats(self,PL,index):
        # Called every iteration to ADD stats into an array.        
        # These arrays will be later copied into a DATAFRAME
        if self.prev_traded_position == 1:
            self.action[index] = self.current_action
        
        elif self.prev_traded_position == -1:
            self.action[index] = self.current_action
        
        elif self.prev_traded_position == 0:
            self.action[index] = self.current_action
        
        self.arr_PL[index] = PL
        self.arr_total_profit[index] = self.total_profit

    
    
    def getData(self):
        # Transfers all the data into the DATAFRAME
        # The constructor is initialised with
        self.data['action'] = self.action
        self.data['P/L'] = self.arr_PL
        self.data['Total profit'] = self.arr_total_profit
        return self.data

    ############### Actions ###############
    def buy(self,current_price,index):
        # PL value initialised to 0, current action set to 'buy'
        # previous traded position is set along with prev traded price
        # Data is saved to later copied into dataframe
        # total profit is returned
        PL = 0 # <----- Default for if currently holding 
        if self.prev_traded_position == 0:
            self.current_action = "buy"
            self.prev_traded_position = 1
            self.prev_traded_price = current_price
            self.saveStats(PL,index)

        elif self.prev_traded_position == 1:
            # Reciving a stroger buy signal, 
            # Changing take profit to reflect that
            # PL = self.prev_traded_position*(current_price - self.prev_traded_price)
            # if PL > 0:
            #     self.take_profit *= 1.02 # <----- EDIT Based on how you wish to scale take_profit
            #     self.stop_loss *= 2
            self.checkStopConditions(current_price,index)
        
        elif self.prev_traded_position == -1:
            # if previous position was 'Sell' then set current action to 'short buy'
            # Calculate PL value
            # Take profit or stop loss value is fetched depending on PL
            # Trade closed and data saved
            self.current_action = "short_buy"
            PL = (self.prev_traded_position*(current_price - self.prev_traded_price))-self.broker_cost
            PL = self.bandPL(PL)
            self.closeTrade(PL)
            self.saveStats(PL,index)

        else: 
            print("Should not be here")
            
        return self.total_profit

    def sell(self,current_price,index):
        # Current action is set based on previous traded position (0->'Short', 1->'Sell', 0->'Hold')
        # previous traded position reset
        # Data saved for later copying into dataframe
        # total profit value returned
        PL = 0 # <----- Default for if currently holding
        if self.prev_traded_position == 0:
            self.current_action = "short"
            self.prev_traded_position = -1
            self.prev_traded_price = current_price
            self.saveStats(PL,index)

        elif self.prev_traded_position == -1:
            # Reciving a stroger sell signal, 
            # Changing stop loss to reflect that
            # self.stop_loss *= 0.5 # <----- EDIT Based on how you wish to scale stop_loss
            self.checkStopConditions(current_price,index)
        
        elif self.prev_traded_position == 1:
            self.current_action = "sell"
            PL = (self.prev_traded_position*(current_price - self.prev_traded_price))-self.broker_cost
            PL = self.bandPL(PL)
            self.closeTrade(PL)
            self.saveStats(PL,index)
        else: 
            print("Should not be here")

        return self.total_profit
    
    
    def checkStopConditions(self,current_price,index):
        # Called from MAIN code when the HOLD signal is received
        # ALSO called by the BUY AND SELL functions when
        # the broker sequentially receives the same signal.
        # current action is set as 'hold'
        # PL value calculated and trade closed
        # total profit returned
        PL = 0
        self.current_action = "hold"
        
        if self.prev_traded_position != 0:
            
            PL = (self.prev_traded_position*(current_price - self.prev_traded_price))-self.broker_cost
            
            if PL > self.take_profit:
                PL = self.bandPL(PL) 
                self.closeTrade(PL)
            elif PL < self.stop_loss:
                PL = self.bandPL(PL)
                self.closeTrade(PL)
        
        self.saveStats(PL,index)
        return self.total_profit
