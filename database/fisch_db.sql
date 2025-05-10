-- Table structure for table `game_appeals`
CREATE TABLE `game_appeals` (
  `appeal_id` int(11) NOT NULL AUTO_INCREMENT,
  `exploiter_id` bigint(20) NOT NULL,
  `ban_reason` varchar(50) NOT NULL,
  `appeal_reason` varchar(1024) NOT NULL,
  `additional_info` varchar(1024) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `submitted_by` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`appeal_id`)
);

-- --------------------------------------------------------

-- Table structure for table `game_reports`
CREATE TABLE `game_reports` (
  `report_id` int(11) NOT NULL AUTO_INCREMENT,
  `exploiter_id` bigint(20) NOT NULL,
  `reason` varchar(500) NOT NULL,
  `evidence` varchar(1024) NOT NULL,
  `additional_info` varchar(1024) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `submitted_by` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`report_id`)
);