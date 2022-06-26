CREATE DEFINER=`root`@`localhost` TRIGGER `voice_data_AFTER_INSERT` AFTER INSERT ON `voice_data` FOR EACH ROW BEGIN
UPDATE charcter SET voice_count=voice_count+1 WHERE charcter.char_name=new.char_name;
END