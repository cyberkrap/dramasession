update sub_blocks set created_utc=0 where created_utc is null;
update exiles set created_utc=0 where created_utc is null;
update sub_subscriptions set created_utc=0 where created_utc is null;
