CREATE TABLE `contacts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `fullname` VARCHAR(255) NULL,
  `phone` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));