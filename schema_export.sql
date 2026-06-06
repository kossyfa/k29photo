--
-- PostgreSQL database dump
--

\restrict FsO86J3xgvFT5hTSlgCdZ2Wx3z49Qc18PV2OfnT2AMhGaWQxfdguElMYRIxu9pV

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: check_comment_owner(); Type: FUNCTION; Schema: public; Owner: k29
--

CREATE FUNCTION public.check_comment_owner() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.owner_id IS NULL THEN
        RETURN NEW;
    END IF;
    IF NEW.owner_id = (
        SELECT a.owner_id FROM photos p
        JOIN albums a ON p.album_id = a.album_id
        WHERE p.photo_id = NEW.photo_id
    ) THEN
        RAISE EXCEPTION 'Δεν μπορείς να σχολιάσεις τη δική σου φωτογραφία!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_comment_owner() OWNER TO k29;

--
-- Name: check_duplicate_friend(); Type: FUNCTION; Schema: public; Owner: k29
--

CREATE FUNCTION public.check_duplicate_friend() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM friends
        WHERE (user_id1 = NEW.user_id1 AND user_id2 = NEW.user_id2)
           OR (user_id1 = NEW.user_id2 AND user_id2 = NEW.user_id1)
    ) THEN
        RAISE EXCEPTION 'Η φιλία αυτή υπάρχει ήδη!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_duplicate_friend() OWNER TO k29;

--
-- Name: check_duplicate_like(); Type: FUNCTION; Schema: public; Owner: k29
--

CREATE FUNCTION public.check_duplicate_like() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM likes
        WHERE user_id = NEW.user_id AND photo_id = NEW.photo_id
    ) THEN
        RAISE EXCEPTION 'Έχεις ήδη κάνει like σε αυτή τη φωτογραφία!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_duplicate_like() OWNER TO k29;

--
-- Name: check_like_owner(); Type: FUNCTION; Schema: public; Owner: k29
--

CREATE FUNCTION public.check_like_owner() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.user_id = (
        SELECT a.owner_id
        FROM photos p
        JOIN albums a ON p.album_id = a.album_id
        WHERE p.photo_id = NEW.photo_id
    ) THEN
        RAISE EXCEPTION 'Δεν μπορείς να κάνεις like στη δική σου φωτογραφία!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_like_owner() OWNER TO k29;

--
-- Name: check_photo_album_owner(); Type: FUNCTION; Schema: public; Owner: k29
--

CREATE FUNCTION public.check_photo_album_owner() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_album_owner INT;
BEGIN
    SELECT owner_id INTO v_album_owner
    FROM albums
    WHERE album_id = NEW.album_id;

    IF v_album_owner IS NULL THEN
        RAISE EXCEPTION 'Το album δεν υπάρχει!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_photo_album_owner() OWNER TO k29;

--
-- Name: check_self_friend(); Type: FUNCTION; Schema: public; Owner: k29
--

CREATE FUNCTION public.check_self_friend() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.user_id1 = NEW.user_id2 THEN
        RAISE EXCEPTION 'Δεν μπορείς να προσθέσεις τον εαυτό σου ως φίλο!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_self_friend() OWNER TO k29;

--
-- Name: normalize_tag_name(); Type: FUNCTION; Schema: public; Owner: k29
--

CREATE FUNCTION public.normalize_tag_name() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.name := LOWER(TRIM(NEW.name));
    IF NEW.name LIKE '% %' THEN
        RAISE EXCEPTION 'Το tag δεν μπορεί να περιέχει κενά!';
    END IF;
    IF NEW.name = '' THEN
        RAISE EXCEPTION 'Το tag δεν μπορεί να είναι κενό!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.normalize_tag_name() OWNER TO k29;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: albums; Type: TABLE; Schema: public; Owner: k29
--

CREATE TABLE public.albums (
    album_id integer NOT NULL,
    name character varying(100) NOT NULL,
    owner_id integer NOT NULL,
    date_created date DEFAULT CURRENT_DATE NOT NULL
);


ALTER TABLE public.albums OWNER TO k29;

--
-- Name: albums_album_id_seq; Type: SEQUENCE; Schema: public; Owner: k29
--

CREATE SEQUENCE public.albums_album_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.albums_album_id_seq OWNER TO k29;

--
-- Name: albums_album_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: k29
--

ALTER SEQUENCE public.albums_album_id_seq OWNED BY public.albums.album_id;


--
-- Name: comments; Type: TABLE; Schema: public; Owner: k29
--

CREATE TABLE public.comments (
    comment_id integer NOT NULL,
    text text NOT NULL,
    owner_id integer,
    photo_id integer NOT NULL,
    post_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.comments OWNER TO k29;

--
-- Name: comments_comment_id_seq; Type: SEQUENCE; Schema: public; Owner: k29
--

CREATE SEQUENCE public.comments_comment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comments_comment_id_seq OWNER TO k29;

--
-- Name: comments_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: k29
--

ALTER SEQUENCE public.comments_comment_id_seq OWNED BY public.comments.comment_id;


--
-- Name: friends; Type: TABLE; Schema: public; Owner: k29
--

CREATE TABLE public.friends (
    user_id1 integer NOT NULL,
    user_id2 integer NOT NULL,
    CONSTRAINT friends_check CHECK ((user_id1 < user_id2))
);


ALTER TABLE public.friends OWNER TO k29;

--
-- Name: likes; Type: TABLE; Schema: public; Owner: k29
--

CREATE TABLE public.likes (
    user_id integer NOT NULL,
    photo_id integer NOT NULL
);


ALTER TABLE public.likes OWNER TO k29;

--
-- Name: photo_tags; Type: TABLE; Schema: public; Owner: k29
--

CREATE TABLE public.photo_tags (
    photo_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.photo_tags OWNER TO k29;

--
-- Name: photos; Type: TABLE; Schema: public; Owner: k29
--

CREATE TABLE public.photos (
    photo_id integer NOT NULL,
    caption character varying(255),
    data bytea NOT NULL,
    album_id integer NOT NULL
);


ALTER TABLE public.photos OWNER TO k29;

--
-- Name: photos_photo_id_seq; Type: SEQUENCE; Schema: public; Owner: k29
--

CREATE SEQUENCE public.photos_photo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.photos_photo_id_seq OWNER TO k29;

--
-- Name: photos_photo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: k29
--

ALTER SEQUENCE public.photos_photo_id_seq OWNED BY public.photos.photo_id;


--
-- Name: tags; Type: TABLE; Schema: public; Owner: k29
--

CREATE TABLE public.tags (
    tag_id integer NOT NULL,
    name character varying(100) NOT NULL,
    CONSTRAINT tags_name_check CHECK (((name)::text = lower((name)::text))),
    CONSTRAINT tags_name_check1 CHECK (((name)::text !~~ '% %'::text))
);


ALTER TABLE public.tags OWNER TO k29;

--
-- Name: tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: k29
--

CREATE SEQUENCE public.tags_tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tags_tag_id_seq OWNER TO k29;

--
-- Name: tags_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: k29
--

ALTER SEQUENCE public.tags_tag_id_seq OWNED BY public.tags.tag_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: k29
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    dob date,
    hometown character varying(100),
    gender character(1),
    password character varying(255) NOT NULL,
    CONSTRAINT users_gender_check CHECK ((gender = ANY (ARRAY['M'::bpchar, 'F'::bpchar, 'O'::bpchar])))
);


ALTER TABLE public.users OWNER TO k29;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: k29
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO k29;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: k29
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: albums album_id; Type: DEFAULT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.albums ALTER COLUMN album_id SET DEFAULT nextval('public.albums_album_id_seq'::regclass);


--
-- Name: comments comment_id; Type: DEFAULT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.comments ALTER COLUMN comment_id SET DEFAULT nextval('public.comments_comment_id_seq'::regclass);


--
-- Name: photos photo_id; Type: DEFAULT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.photos ALTER COLUMN photo_id SET DEFAULT nextval('public.photos_photo_id_seq'::regclass);


--
-- Name: tags tag_id; Type: DEFAULT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.tags ALTER COLUMN tag_id SET DEFAULT nextval('public.tags_tag_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: albums albums_pkey; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.albums
    ADD CONSTRAINT albums_pkey PRIMARY KEY (album_id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (comment_id);


--
-- Name: friends friends_pkey; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_pkey PRIMARY KEY (user_id1, user_id2);


--
-- Name: likes likes_pkey; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT likes_pkey PRIMARY KEY (user_id, photo_id);


--
-- Name: photo_tags photo_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.photo_tags
    ADD CONSTRAINT photo_tags_pkey PRIMARY KEY (photo_id, tag_id);


--
-- Name: photos photos_pkey; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_pkey PRIMARY KEY (photo_id);


--
-- Name: tags tags_name_key; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_name_key UNIQUE (name);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (tag_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: comments trg_check_comment_owner; Type: TRIGGER; Schema: public; Owner: k29
--

CREATE TRIGGER trg_check_comment_owner BEFORE INSERT ON public.comments FOR EACH ROW EXECUTE FUNCTION public.check_comment_owner();


--
-- Name: friends trg_check_duplicate_friend; Type: TRIGGER; Schema: public; Owner: k29
--

CREATE TRIGGER trg_check_duplicate_friend BEFORE INSERT ON public.friends FOR EACH ROW EXECUTE FUNCTION public.check_duplicate_friend();


--
-- Name: likes trg_check_duplicate_like; Type: TRIGGER; Schema: public; Owner: k29
--

CREATE TRIGGER trg_check_duplicate_like BEFORE INSERT ON public.likes FOR EACH ROW EXECUTE FUNCTION public.check_duplicate_like();


--
-- Name: likes trg_check_like_owner; Type: TRIGGER; Schema: public; Owner: k29
--

CREATE TRIGGER trg_check_like_owner BEFORE INSERT ON public.likes FOR EACH ROW EXECUTE FUNCTION public.check_like_owner();


--
-- Name: photos trg_check_photo_album_owner; Type: TRIGGER; Schema: public; Owner: k29
--

CREATE TRIGGER trg_check_photo_album_owner BEFORE INSERT ON public.photos FOR EACH ROW EXECUTE FUNCTION public.check_photo_album_owner();


--
-- Name: friends trg_check_self_friend; Type: TRIGGER; Schema: public; Owner: k29
--

CREATE TRIGGER trg_check_self_friend BEFORE INSERT ON public.friends FOR EACH ROW EXECUTE FUNCTION public.check_self_friend();


--
-- Name: tags trg_normalize_tag_name; Type: TRIGGER; Schema: public; Owner: k29
--

CREATE TRIGGER trg_normalize_tag_name BEFORE INSERT OR UPDATE ON public.tags FOR EACH ROW EXECUTE FUNCTION public.normalize_tag_name();


--
-- Name: albums albums_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.albums
    ADD CONSTRAINT albums_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: comments comments_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: comments comments_photo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_photo_id_fkey FOREIGN KEY (photo_id) REFERENCES public.photos(photo_id) ON DELETE CASCADE;


--
-- Name: friends friends_user_id1_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_user_id1_fkey FOREIGN KEY (user_id1) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: friends friends_user_id2_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_user_id2_fkey FOREIGN KEY (user_id2) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: likes likes_photo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT likes_photo_id_fkey FOREIGN KEY (photo_id) REFERENCES public.photos(photo_id) ON DELETE CASCADE;


--
-- Name: likes likes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: photo_tags photo_tags_photo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.photo_tags
    ADD CONSTRAINT photo_tags_photo_id_fkey FOREIGN KEY (photo_id) REFERENCES public.photos(photo_id) ON DELETE CASCADE;


--
-- Name: photo_tags photo_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.photo_tags
    ADD CONSTRAINT photo_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(tag_id) ON DELETE CASCADE;


--
-- Name: photos photos_album_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: k29
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_album_id_fkey FOREIGN KEY (album_id) REFERENCES public.albums(album_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict FsO86J3xgvFT5hTSlgCdZ2Wx3z49Qc18PV2OfnT2AMhGaWQxfdguElMYRIxu9pV

