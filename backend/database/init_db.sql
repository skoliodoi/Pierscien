CREATE TABLE IF NOT EXISTS `p_benefity` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `mocarz_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `okres_rozliczenia` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `imie_i_nazwisko` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pesel` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `centrum_operacyjne` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rodzaj` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `kwota` float COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `komentarz` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `osoba_wysylajaca` varchar(255) COLLATE utf8mb4_unicode_ci,
  `data_wyslania` timestamp COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_bledy` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `missing_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mocarz_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `imie` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nazwisko` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `profil` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `projekt_kod_z_pliku` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `projekt_nazwa_z_mocarza` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nazwa_pliku` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `problem` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `czas_utworzenia` timestamp NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_do_zatwierdzenia` (
  `zatwierdzenie_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `project_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lokalizacja` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `okres_rozliczenia` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `osoba_wysylajaca` varchar(255) COLLATE utf8mb4_unicode_ci,
  `dane` json,
  `data_wyslania` timestamp COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`zatwierdzenie_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_zatwierdzone_json` (
  `zatwierdzenie_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `project_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lokalizacja` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `okres_rozliczenia` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `osoba_wysylajaca` varchar(255) COLLATE utf8mb4_unicode_ci,
  `dane` json,
  `data_wyslania` timestamp COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `osoba_zatwierdzajaca` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_zatwierdzenia` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`zatwierdzenie_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_anulowane_json` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `zatwierdzenie_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `project_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lokalizacja` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `okres_rozliczenia` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `osoba_wysylajaca` varchar(255) COLLATE utf8mb4_unicode_ci,
  `dane` json,
  `data_wyslania` timestamp COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `osoba_zatwierdzajaca` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_zatwierdzenia` timestamp NULL DEFAULT NULL,
  `osoba_anulujaca` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_anulowania` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_odrzucone` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `project_code` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `project_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `okres_rozliczenia` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kto_wysylal` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_wyslania` timestamp COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kto_usunal` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `powod_usuniecia` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_usuniecia` timestamp COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `odrzucenie` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT 'N',
  `powod_odrzucenia` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_track_logins` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `login` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `czas_logowania` timestamp COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `mocarz_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `login` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mail` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `access` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_zatwierdzacze` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `login` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lokalizacja` varchar(50) COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_zatwierdzone` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `zatwierdzenie_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nazwa_pliku` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lokalizacja` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `okres_rozliczenia` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mocarz_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `imie_i_nazwisko` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `PESEL` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_pracy` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `suma_godzin` float COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `w_tym_nieefektywne` float COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `w_tym_szkoleniowe` float NULL DEFAULT NULL,
  `uwagi` varchar(1000) DEFAULT NULL,
  `stawka_za_dzien` float NULL DEFAULT NULL,
  `rodzaj_umowy` varchar(255) DEFAULT NULL,
  `kwota` float COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `koszt` float COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kwota_z_kosztem` float COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `osoba_wysylajaca` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_wyslania` timestamp NULL DEFAULT NULL,
  `osoba_zatwierdzajaca` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_zatwierdzenia` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `p_zatwierdzone_bonusy` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `zatwierdzenie_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nazwa_pliku` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lokalizacja` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `okres_rozliczenia` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mocarz_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `imie_i_nazwisko` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `PESEL` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kwota` float COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kategoria` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `komentarz` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `osoba_wysylajaca` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_wyslania` timestamp NULL DEFAULT NULL,
  `osoba_zatwierdzajaca` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_zatwierdzenia` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;






