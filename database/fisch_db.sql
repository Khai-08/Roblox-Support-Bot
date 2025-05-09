-- Table structure for table `game_appeals`
CREATE TABLE `game_appeals` (
  `appeal_id` int(11) NOT NULL AUTO_INCREMENT,
  `exploiter_id` bigint(20) NOT NULL,
  `ban_reason` text NOT NULL,
  `appeal_reason` text NOT NULL,
  `additional_info` text DEFAULT NULL,
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
  `reason` varchar(255) NOT NULL,
  `evidence` text NOT NULL,
  `additional_info` text DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `submitted_by` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`report_id`)
);