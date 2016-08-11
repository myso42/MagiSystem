%THOMAS J. GEORGE and CHUAN-YANG HWANG, The 52-Week High and Momentum
%Investing,JF 2014
%measurement of momentum: price relative to 52(MeasurePeriod)-week high
function[W,L,M,t,p,Rhigh,Rlow,Rmom]=Week_High(J,K,NumTrade,MeasurePeriod) 

Price=xlsread('test.xlsx');  % panel data: T*N
O=size(Price,1);
Return=diff(Price)./Price(1:O-1,:);

Prices=Price(2:O,:);

T=size(Return,1);
ReturnLow=zeros(T-J-1,K);   %stock sale position return
ReturnHigh=zeros(T-J-1,K);   %stock hold position return

for t=1:T-J-K
    for i=1:K
        MaxPrices=max(Prices(t:t+MeasurePeriod-1,:));
        PropPrice=Prices(t+J-1,:)./MaxPrices;
        [SortRatio,StockIndex]=sort(PropPrice); 
        N1=isnan(SortRatio);  %Is it not a number?
        N2=size(Return,2)-sum(N1,2);
        N3=[1:NumTrade,N2-NumTrade+1:N2];
        TradeIndex=StockIndex(N3);
        ReturnLow(t+i-1,i)=mean(Return(t+J+i,TradeIndex(1:NumTrade)));
        ReturnHigh(t+i-1,i)=mean(Return(t+J+i,TradeIndex(NumTrade+1:2*NumTrade)));
    end
end

 for q=1:(K-1)
   for i=1:q
        t=T-J-q;
        MaxPrices=max(Prices(t:t+MeasurePeriod-1,:));
        PropPrice=Prices(t+J-1,:)./MaxPrices;
        [SortRatio,StockIndex]=sort(PropPrice); 
        N1=isnan(SortRatio);  %Is it not a number?
        N2=size(Return,2)-sum(N1,2);
        N3=[1:NumTrade,N2-NumTrade+1:N2];
        TradeIndex=StockIndex(N3);
        ReturnLow(t+i-1,i)=mean(Return(t+J+i,TradeIndex(1:NumTrade)));
        ReturnHigh(t+i-1,i)=mean(Return(t+J+i,TradeIndex(NumTrade+1:2*NumTrade)));
    end
end

Rhigh=mean(ReturnHigh,2);  %time series: buy position return
Rlow=mean(ReturnLow,2);
Rmom= Rhigh-Rlow;          %measure of momentum
W=mean(Rhigh(K:T-J-1,:));  %average winning 
L=mean(Rlow(K:T-J-1,:));   
M=W-L;
[t,p]=ttest(Rhigh-Rlow);

end