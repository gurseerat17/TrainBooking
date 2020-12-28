create table availabletrains(
    train_no int ,
    train_date date ,
    no_of_ac_coaches int,
    no_of_slp_coaches int,
    primary key(train_no,train_date)
);

create table bookingagents(id serial primary key,
						  name varchar(20),
						   password varchar(20),
						  creditcard varchar(20),
						  address text
						  );
						  
create table bookedtickets(pnr varchar(20) primary key,
			   train_no varchar(20),
			   train_date varchar(20),
			   passenger_no int,
			   booking_ag text
			   )
