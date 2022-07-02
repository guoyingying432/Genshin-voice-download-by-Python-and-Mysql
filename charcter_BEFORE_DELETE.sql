CREATE DEFINER=`root`@`localhost` TRIGGER `charcter_BEFORE_DELETE` 
BEFORE DELETE ON `charcter` FOR EACH ROW BEGIN
delete from voice_data where voice_data.char_name=old.char_name;
END