CREATE schema if not exists sentiment;


drop table if exists sentiment.keyword;
drop table if exists sentiment.sentiment_values;
drop table if exists sentiment.articles;

create table sentiment.articles (
	id serial primary key,
	url varchar not null,
	title varchar not null,
	source varchar not null,
	created timestamp not null default now(),
	modified timestamp
);


create table sentiment.keyword (
	id serial primary key,
	article_id int not null,
	keyword varchar,
	created timestamp not null default now(),
	modified timestamp,
	constraint fk_keyword_article foreign key (article_id) references sentiment.articles(id)
);

create table sentiment.sentiment_values (
	id serial primary key,
	article_id int not null,
	sentiment int,
	created timestamp not null default now(),
	modified timestamp,
	constraint fk_sentiment_values_article foreign key (article_id) references sentiment.articles(id)
);
