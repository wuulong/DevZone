# Author: wuulong@gmail.com
# LICENSE: MIT
# Document: https://docs.google.com/document/d/1CZtE2BP9_ua9ZD0BIfI5nt6NX_pPpQBh4yjV9SH2m98/edit#bookmark=id.hba2bixdny2p
library("xts")
library(dplyr)
version="0.1"
#load from commutag
#setwd("/Users/wuulong/github/DevZone/Codes")
dataset_id<-"6322c60410be156d74c8d2a8" #舊港島
if(1){ # 線上json取得，轉換成類似 CSV 格式，轉出 info_sim.csv
  url_str=paste("https://commutag.agawork.tw/dataset/list-image?all=1&dataset=",dataset_id,sep="")
  con <- url(url_str)
  txt <- readLines(con)
  commlist<-jsonlite::fromJSON(txt)
  info_url<-commlist$data
  info_sim<-info_url

}else{
  info <- read.csv(file = paste(getwd(),"/info.csv",sep=""))
}

if(1){ # group_by for 圓餅圖
  pie_data <- info_sim %>% group_by(formReply$yjx5mtk5j4n) %>% summarise(cnt = n()) #類別
  pie_data$label <- paste(pie_data$value," " , sprintf("%.2f",  pie_data$cnt/sum(pie_data$cnt)*100),"%")
  pie(pie_data$cnt,labels=pie_data$label,family="黑體-繁 中黑") 
}



