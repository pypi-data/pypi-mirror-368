

main_utr_distribution_workflow<-function(all_leads,campaign_name,round_robin=T,return_input=F,person_filter=NULL){
  log_info("### >>>> UTR Distribution <<<<< #####")
  a4<-noquote(paste("'Sales_Rep'",sep=','))


  status.counts1<-getPipelineCounts(a4,campaign_name) %>% filter(category_campaign %in% campaign_name)  %>%
   mutate(dd=lubridate::ymd_hms(ddate) %>% as.Date()) %>% distinct(dd,open_user_id,.keep_all=T)

 # status.counts1 <- status.counts1 %>% dplyr::filter(!grepl("Derek Seym",open_user_id))

  print(status.counts1)

  same.day4<- combine_active_inactive(status.counts1,all_leads)

  if (nrow(same.day4)==0){
    return(NULL)
  }

  if (return_input==T)
    return(same.day4)

  sales.name=status.counts1$open_user_id %>% unique()

  log_info("Running round-robin distribution")
  finaldf<-dist_round_robin(same.day4,sales.name)

  if (is.null(finaldf)){
    log_info("No UTRs to distribute")
    return(NULL)
  }
  log_info("Before:")
  print(table(same.day4$open_user_id))
  print(table(same.day4$status))

  log_info("After:")
  print(table(finaldf$open_user_id))
  print(table(finaldf$status))


  savefile=glue::glue("~klevonas/r_work/report_data/UTR.salesmen.distribution.{campaign_name}.RDS")
  saveRDS(list(input=same.day4,sales.name=sales.name,finaldf=finaldf,all_leads=all_leads),savefile)
  log_info(glue("Saved backup file for UTR: {savefile}"))
  return(finaldf)


}

dist_round_robin<-function(dat,sales.name){

  sales.name=sample(sales.name)

  if(nrow(dat)==0){
    return(NULL)
  }

  res=data.frame()

   while(nrow(dat)>0){
    for (p in sales.name){
      if (nrow(dat)>0){
     dplyr::sample_n(dat,1) ->rec
      rec <- rec  %>% dplyr::filter(user_id!=p) %>%
        dplyr::mutate(closer_id=p,open_user_id=p,user_id=p) %>%
        dplyr::mutate(status="New",team_id="Voice")
      dat<- dplyr::anti_join(dat,rec,by="id")
      res<-plyr::rbind.fill(rec,res)
      }
    }
  }
    return(res)
}


m_leadsActivesalesguys<-function(status.counts1, all_leads, x, stts,lowerlimit,upperlimit)
{
  firstresults <- status.counts1 %>% filter(!open_user_id %in%
                                              c("Drew Cox", "Patrick Adler", "Administrator", "Marc Spiegel")) %>%
    filter(active %in% c(x))
  same.day2 <- all_leads %>% filter(open_user_id %in% firstresults$open_user_id)
  same.day2 <- same.day2 %>% filter(source_date < Sys.Date() -
                                      lowerlimit &
                                      source_date >= Sys.Date() - upperlimit)
  same.day2 <- same.day2 %>% filter(status %in% stts)
  same.day2$activity_date_deadline <- as.Date(same.day2$activity_date_deadline)
  same.day2 <- same.day2 %>% filter(activity_date_deadline <
                                      Sys.Date() - 4 | is.na(activity_date_deadline))
  same.day2 <- same.day2 %>% filter(!is.na(source_date))
  return(same.day2)
}

combine_active_inactive<-function(status.counts1,all_leads){

  #### finding all leads from active sales reps to distribute
  log_info("finding all leads from active sales reps to distribute")
  x<-'True';lowerlimit<-0;upperlimit<-30;stts<-c("Utr","Call Back")
  sd2<-m_leadsActivesalesguys(status.counts1,all_leads,x,stts,lowerlimit,upperlimit)
  x=nrow(sd2)
  log_info(glue("Leads found active to distribute = {x}"))
  #### finding all leads from inactive sales reps to distribute
  x<-'False'
  lowerlimit<-0;upperlimit<-30;stts<-c("Utr","Call Back","Full Pitch Follow Up","Full Pitch Follow Up ","New")
  sd3<-m_leadsActivesalesguys(status.counts1,all_leads,x,stts,lowerlimit,upperlimit)
  log_info(glue("Leads (from inactive) found to distribute = {nrow(sd3)}"))

  ##Combine before distribution
  log_info("Combining active and inactive leads")
  same.day4<-rbind(sd2, sd3)
  log_info(glue("Final Combined = {nrow(same.day4)}"))

  return(same.day4)

}