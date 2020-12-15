drop database mydb;

-- Создание базы данных
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`students`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`students` (
  `id_student` INT NOT NULL,
  `name` VARCHAR(30) NOT NULL,
  `surname` VARCHAR(30) NOT NULL,
  `middle_name` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`id_student`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`teachers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`teachers` (
  `id_teacher` INT NOT NULL,
  `name` VARCHAR(30) NOT NULL,
  `surname` VARCHAR(30) NOT NULL,
  `middle_name` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`id_teacher`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`subjects`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`subjects` (
  `id_subject` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `info` VARCHAR(500) NOT NULL,
  `id_teacher` INT NULL,
  PRIMARY KEY (`id_subject`),
  INDEX `fk_subjects_teachers1_idx` (`id_teacher` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC),
  CONSTRAINT `fk_subjects_teachers1`
    FOREIGN KEY (`id_teacher`)
    REFERENCES `mydb`.`teachers` (`id_teacher`)
    ON DELETE SET NULL
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`student_subject`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`student_subject` (
  `id_student` INT NOT NULL,
  `id_subject` INT NOT NULL,
  INDEX `fk_student_subject_students1_idx` (`id_student` ASC),
  INDEX `fk_student_subject_subjects1_idx` (`id_subject` ASC),
  CONSTRAINT `fk_student_subject_students1`
    FOREIGN KEY (`id_student`)
    REFERENCES `mydb`.`students` (`id_student`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_student_subject_subjects1`
    FOREIGN KEY (`id_subject`)
    REFERENCES `mydb`.`subjects` (`id_subject`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`tasks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`tasks` (
  `id_task` INT NOT NULL AUTO_INCREMENT,
  `info` VARCHAR(500) NOT NULL,
  `dead_line` DATE NOT NULL,
  `id_subject` INT NOT NULL,
  PRIMARY KEY (`id_task`),
  INDEX `fk_tasks_subjects1_idx` (`id_subject` ASC),
  CONSTRAINT `fk_tasks_subjects1`
    FOREIGN KEY (`id_subject`)
    REFERENCES `mydb`.`subjects` (`id_subject`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`lessons`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`lessons` (
  `id_lesson` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `id_subject` INT NOT NULL,
  PRIMARY KEY (`id_lesson`),
  INDEX `fk_lessons_subjects1_idx` (`id_subject` ASC),
  CONSTRAINT `fk_lessons_subjects1`
    FOREIGN KEY (`id_subject`)
    REFERENCES `mydb`.`subjects` (`id_subject`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`lesson_student`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`lesson_student` (
  `id_lesson` INT NOT NULL,
  `id_student` INT NOT NULL,
  INDEX `fk_lesson_studsub_lesson1_idx` (`id_lesson` ASC),
  INDEX `fk_lesson_studsub_students1_idx` (`id_student` ASC),
  CONSTRAINT `fk_lesson_studsub_lesson1`
    FOREIGN KEY (`id_lesson`)
    REFERENCES `mydb`.`lessons` (`id_lesson`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_lesson_studsub_students1`
    FOREIGN KEY (`id_student`)
    REFERENCES `mydb`.`students` (`id_student`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`literatures`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`literatures` (
  `id_literature` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(500) NOT NULL,
  `id_subject` INT NOT NULL,
  INDEX `fk_literature_subjects_idx` (`id_subject` ASC),
  PRIMARY KEY (`id_literature`),
  CONSTRAINT `fk_literature_subjects`
    FOREIGN KEY (`id_subject`)
    REFERENCES `mydb`.`subjects` (`id_subject`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`task_student`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`task_student` (
  `id_task` INT NOT NULL,
  `id_student` INT NOT NULL,
  `point` INT NOT NULL DEFAULT 0,
  INDEX `fk_studsub_task_tasks1_idx` (`id_task` ASC),
  INDEX `fk_studsub_task_students1_idx` (`id_student` ASC),
  CONSTRAINT `fk_studsub_task_tasks1`
    FOREIGN KEY (`id_task`)
    REFERENCES `mydb`.`tasks` (`id_task`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_studsub_task_students1`
    FOREIGN KEY (`id_student`)
    REFERENCES `mydb`.`students` (`id_student`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
-- Конец создаия базы

-- Создание общих процедур
drop procedure if exists registration_user;
DELIMITER // 
CREATE PROCEDURE `registration_user` (in id int, in user_name varchar(30), in user_surname varchar(30), in user_middle_name varchar(30),  in is_teacher boolean)
BEGIN 
    if is_teacher then
		insert teachers(id_teacher, name, surname, middle_name) value (id, user_name, user_surname, user_middle_name);
	else 
		insert students(id_student, name, surname, middle_name) value (id, user_name, user_surname, user_middle_name);
	end if;
END// 

drop procedure if exists delete_user;

DELIMITER // 
CREATE PROCEDURE `delete_user` (in id int)
BEGIN
	if (select id_teacher from teachers where id_teacher = id) then
		delete from teacher where id_teacher = id;
	elseif (select id_student from students where id_student = id) then
		delete from students where id_student = id;
	end if;
END// 

-- Создание процедур для студента
drop procedure if exists entry_to_course;

DELIMITER // 
CREATE PROCEDURE `entry_to_course` (in id_user int, in name_course varchar(30))
BEGIN 
	declare done, id_course int;
	DECLARE curs cursor for select id_subject from subjects where name = name_course;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    open curs;
    curs_loop:
		loop fetch curs into id_course;
			if done = 1 then
				leave curs_loop;
			end if;
			insert into student_subject (id_student, id_subject) value (id_user, id_course);
		end loop curs_loop;
	close curs;
END//

-- Создание процедур преподователя
drop procedure if exists add_home_work;

DELIMITER // 
CREATE PROCEDURE `add_home_work` (in id_user int, in name_course varchar(45), in info varchar(500), in in_dead_line date)
BEGIN 
	declare done, id_course int;
	DECLARE curs cursor for select s.id_subject from subjects as s left join teachers as t on s.id_teacher=t.id_teacher where s.name=name_course and t.id_teacher=id_user;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    open curs;
    curs_loop:
		loop fetch curs into id_course;
			if done = 1 then
				leave curs_loop;
			end if;
            insert into tasks(info, dead_line, id_subject) value (info, in_dead_line, id_course);
		end loop curs_loop;
	close curs;
END//

drop procedure if exists add_literature;

DELIMITER // 
CREATE PROCEDURE `add_literature` (in id_user int, in name_course varchar(45), in literature varchar(500))
BEGIN 
	declare done, id_course int;
	DECLARE curs cursor for select s.id_subject from subjects as s left join teachers as t on s.id_teacher=t.id_teacher where s.name=name_course and t.id_teacher=id_user;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    open curs;
    curs_loop:
		loop fetch curs into id_course;
			if done = 1 then
				leave curs_loop;
			end if;
            insert into literatures(name, id_subject) value (literature, id_course);
		end loop curs_loop;
	close curs;
END//

drop procedure if exists edit_home_work;

DELIMITER // 
CREATE PROCEDURE `edit_home_work` (in id_user int, in name_course varchar(45), in number_task int, in new_info varchar(500), in new_dead_line date)
BEGIN 
	declare done, real_id_task, num_task int;
	DECLARE curs cursor for select ts.id_task from subjects as s 
								left join teachers as t
									on s.id_teacher=t.id_teacher
								left join tasks as ts
									on s.id_subject=ts.id_subject where (s.name=name_course and t.id_teacher=id_user);
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    
    set num_task = 0;
    open curs;
    curs_loop:
		loop fetch curs into real_id_task;
			if done = 1 then
				leave curs_loop;
			end if;
            if num_task = number_task then
				update tasks set info = new_info, dead_line = new_dead_line where id_task = real_id_task;
			end if;
            set num_task = num_task + 1;
		end loop curs_loop;
	close curs;
END//

drop procedure if exists edit_literature;

DELIMITER // 
CREATE PROCEDURE `edit_literature` (in id_user int, in name_course varchar(45), in number_literature int, in new_literature varchar(500))
BEGIN 
	declare done, real_id_literature, num_literature int;
	DECLARE curs cursor for select id_literature from subjects as s 
									left join teachers as t
										on s.id_teacher=t.id_teacher
									left join literatures as l
										on s.id_subject=l.id_subject where (s.name=name_course and t.id_teacher=id_user);
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    
    set num_literature = 0;
    open curs;
    curs_loop:
		loop fetch curs into real_id_literature;
			if done = 1 then
				leave curs_loop;
			end if;
            if num_literature = number_literature then
				update literatures set literatures.name = new_literature where id_literature = real_id_literature;
			end if;
            set num_literature = num_literature + 1;
		end loop curs_loop;
	close curs;
END//

drop procedure if exists edit_info_course;

DELIMITER // 
CREATE PROCEDURE `edit_info_course` (in id_user int, in name_course varchar(45), in new_info varchar(500))
BEGIN 
	declare done, id_course int;
	DECLARE curs cursor for select s.id_subject from subjects as s left join teachers as t on s.id_teacher=t.id_teacher where s.name=name_course and t.id_teacher=id_user;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    open curs;
    curs_loop:
		loop fetch curs into id_course;
			if done = 1 then
				leave curs_loop;
			end if;
            update subjects set info = new_info where id_subject = id_course;
		end loop curs_loop;
	close curs;
END// 

drop procedure if exists add_lesson;

DELIMITER // 
CREATE PROCEDURE `add_lesson` (in id_user int, in name_course varchar(45), in date_lesson date)
BEGIN 
	declare done, id_course int;
	DECLARE curs cursor for select s.id_subject from subjects as s left join teachers as t on s.id_teacher=t.id_teacher where s.name=name_course and t.id_teacher=id_user;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    open curs;
    curs_loop:
		loop fetch curs into id_course;
			if done = 1 then
				leave curs_loop;
			end if;
            insert into lessons(date, id_subject) value (date_lesson, id_course);
		end loop curs_loop;
	close curs;
END//



drop procedure if exists mark_completed_task;

DELIMITER // 
CREATE PROCEDURE `mark_completed_task` (in id_user int, in name_course varchar(45), in id_task int, in id_student int, in point int)
BEGIN 
	declare done, id_task_this int;
	DECLARE curs cursor for 
		select tas.id_task from
			subjects as s
				left join
			teachers as t
					on s.id_teacher=t.id_teacher
				left join
			tasks as tas
					on tas.id_subject = s.id_subject
		where s.name=name_course and t.id_teacher=id_user and tas.id_task = id_task;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    open curs;
    curs_loop:
		loop fetch curs into id_task_this;
			if done = 1 then
				leave curs_loop;
			end if;
            insert into task_student(id_task, id_student, point) value (id_task_this, id_student, point);
		end loop curs_loop;
	close curs;
END//

drop procedure if exists mark_student_in_class;

DELIMITER // 
CREATE PROCEDURE `mark_student_in_class` (in id_user int, in name_course varchar(45), in id_lesson int, in id_student int)
BEGIN 
	declare done, id_lesson_this int;
	DECLARE curs cursor for 
		select l.id_lesson from
			subjects as s
				left join
			teachers as t
					on s.id_teacher=t.id_teacher
				left join
			lessons as l
					on l.id_subject = s.id_subject
		where s.name=name_course and t.id_teacher=id_user and l.id_lesson = id_lesson;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    open curs;
    curs_loop:
		loop fetch curs into id_lesson_this;
			if done = 1 then
				leave curs_loop;
			end if;
            insert into lesson_student(id_lesson, id_student) value (id_lesson_this, id_student);
		end loop curs_loop;
	close curs;
END//


-- Создание представлений
create or replace
view view_rating_student
as
select id_student, sum(point) as rating from task_student group by id_student;

create or replace
view view_task_student
as
select s.id_student, t_s.point, t.id_subject, t.id_task, t.info, t.dead_line 
from students as s
	left join task_student as t_s
		on s.id_student=t_s.id_student
	left join tasks as t
		on t_s.id_task=t.id_task;
        
create or replace
view view_lesson_student
as
select s.id_student, l.id_lesson, l.date, l.id_subject
from students as s
	left join lesson_student as l_s
		on s.id_student=l_s.id_student
	left join lessons as l
		on l_s.id_lesson=l.id_lesson;

create or replace
view view_task_subject
as
select s.id_subject, s.name as name_subject, s.id_teacher, t.id_task, t.info, t.dead_line from subjects as s
	left join tasks as t
		on t.id_subject=s.id_subject;

create or replace
view view_student_subject
as
select
	sub.id_subject,
    sub.name as name_subject,
    sub.id_teacher,
    t.name as name_teacher,
    t.surname as surname_teacher,
    t.middle_name as middle_name_teacher,
    stud.id_student,
    stud.name as name_student,
    stud.surname as surname_student,
    stud.middle_name as middle_name_student,
    dop.rating
from subjects as sub
	left join teachers as t
		on t.id_teacher=sub.id_teacher
	left join student_subject as s_s
		on sub.id_subject = s_s.id_subject
	left join students as stud
		on stud.id_student = s_s.id_student
	left join view_rating_student as dop
		on dop.id_student = stud.id_student;
        
create or replace
view view_subject_lesson
as
select s.id_subject, s.name as name_subject, s.id_teacher, l.id_lesson, l.date as date_lesson from subjects as s
	left join lessons as l
		on s.id_subject=l.id_subject;
        
create or replace
view view_info_subject
as
select s.id_subject,
	   s.name as name_subject,
       s.info,
       t.name as name_teacher,
       t.surname as surname_teacher,
       t.middle_name as middle_name_teacher,
       l.id_literature,
       l.name as name_literature
from subjects as s
		left join teachers as t
			on s.id_teacher=t.id_teacher
		left join literatures as l
			on l.id_subject=s.id_subject;