ALTER TABLE buckely_candidate ADD `total_expenditures` numeric(19, 2);
ALTER TABLE buckely_candidate ADD `expenditures_supporting` numeric(19, 2);
ALTER TABLE buckely_candidate ADD `expenditures_opposing` numeric(19, 2);
CREATE TABLE `buckley_expenditure_electioneering_candidates` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `expenditure_id` integer NOT NULL,
    `candidate_id` integer NOT NULL,
    UNIQUE (`expenditure_id`, `candidate_id`)
);
ALTER TABLE buckley_expenditure CHANGE candidate_id candidate_id integer;
ALTER TABLE buckley_expenditure ADD `electioneering_communication` bool NOT NULL;
ALTER TABLE `buckley_expenditure_electioneering_candidates` ADD CONSTRAINT `expenditure_id_refs_id_f9810d66` FOREIGN KEY (`expenditure_id`) REFERENCES `buckley_expenditure` (`id`);
CREATE INDEX `buckley_expenditure_6c1886de` ON `buckley_expenditure` (`candidate_id`);
