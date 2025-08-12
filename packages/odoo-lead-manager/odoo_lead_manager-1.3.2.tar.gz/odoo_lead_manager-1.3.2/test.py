searchparams_all=[["|",['is_company', '=', True],['is_company', '=', False]]]
fields=['name', 'phone', 'email','commercial_company_name','create_date','id','is_company','opportunity_ids','invoice_ids']
sres=models.execute_kw(db, uid, password,'res.partner', 'search_read',searchparams_all,
      {'fields': fields})
