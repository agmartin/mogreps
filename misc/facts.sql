
BEGIN;
CREATE SEQUENCE public.fact_air_temp_1_id_seq
    START 1
COMMIT;

BEGIN;

CREATE TABLE IF NOT EXISTS public.fact_air_temp_1 (
    id bigint DEFAULT nextval('fact_air_temp_1_id_seq'::regclass) NOT NULL,
    date_id bigint NOT NULL,
    lat_id bigint NOT NULL,
    lon_id bigint NOT NULL,
    model_id bigint NOT NULL,
    meta_id bigint NOT NULL,
    temp_value numeric NOT NULL,
    PRIMARY KEY(id)
);

COMMIT;



ALTER TABLE public.fact_air_temp_1
ADD FOREIGN KEY (date_id)
  REFERENCES public.dim_date (id)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE public.fact_air_temp_1
ADD FOREIGN KEY (lat_id)
  REFERENCES public.dim_lat (id)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE public.fact_air_temp_1
ADD FOREIGN KEY (lon_id)
  REFERENCES public.dim_lon (id)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE public.fact_air_temp_1
ADD FOREIGN KEY (meta_id)
  REFERENCES public.dim_meta (id)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE public.fact_air_temp_1
ADD FOREIGN KEY (model_id)
  REFERENCES public.dim_model (id)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

