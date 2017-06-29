CREATE TABLE IF NOT EXISTS `mm_site` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `url2` varchar(255) NOT NULL,
  `schedule` varchar(100) DEFAULT NULL COMMENT 'ex. * * * * *',
  `notification` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `enable` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `comment` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `enable` (`enable`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8;

CREATE TABLE IF NOT EXISTS `mm_option` (
  `site_id` int(10) unsigned NOT NULL,
  `model` enum('NONE', 'XML','DOM', 'ATOM') DEFAULT NULL,
  `query_entry` varchar(255) DEFAULT NULL,
  `query_id` varchar(255) DEFAULT NULL,
  `query_title` varchar(255) DEFAULT NULL,
  `query_link` varchar(255) DEFAULT NULL,
  `query_content` varchar(255) DEFAULT NULL,
  `options` varchar(255) DEFAULT NULL,
  `start_tag` varchar(255) DEFAULT NULL,
  `end_tag` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`site_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8;

CREATE TABLE IF NOT EXISTS `mm_updates` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `site_id` int(10) unsigned NOT NULL,
  `url` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content` text,
  `hash` varchar(32) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `site_id` (`site_id`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8;
