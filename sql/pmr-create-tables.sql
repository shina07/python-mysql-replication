use pmr;

CREATE TABLES IF NOT EXISTS `execution_history` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `execution_id` int(11) NOT NULL,
    `start_time` datetime NOT NULL,
    `end_time` datetime NULL,
    `insert_time` datetime NOT NULL,
    `update_time` datetime NULL,
    `status` varchar(255) NOT NULL,
    `error_message` text,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
