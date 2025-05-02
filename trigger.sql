CREATE TRIGGER prevent_duplicate BEFORE INSERT ON RedTiger_device
FOR EACH ROW 
BEGIN
    SET @found = NULL;
    SELECT 
        deviceID INTO @found
    FROM `RedTiger_device`
    WHERE brand = NEW.brand AND model = NEW.model AND line = NEW.line;

    IF @found IS NOT NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Device already in table';
    END IF;
END
