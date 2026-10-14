function results = Bianca_spiel_v4(varargin)
	% function should be called without arguments -> default
	% function can be given an argument which is a specific combination
	% (or, more precisely, the column number of my
	% all_possible_combination-matrix)

	% two empty lines
	disp(' ')
	disp(' ')

	display_on	= false; % false = status information only now and then (very sparse), or true = after every combination (only useful for debugging)

	death		= 0; % counter for "death" results
	skip		= 0; % counter for skipped combinations (search mode only)

	% set initial values
	happy_start			= 5;
	circularity_start	= 0;
	money_start			= 5;
	
	max_mstrings		= 13; % aus maximal 12 Teilen besteht ein Messagestring plus "death" message
	max_text_length		= 6;
	
	% declare array variables
	circle_vec	= [];
	happy_vec	= [];
	money_vec	= [];
	death_cell	= {}; % this array stores all step combinations which results in "death"

	death_occured_in		= NaN; % These two variables are needed to save time: If a certain step results in "death",
	% all steps after that, in all combinations, are irrelevant
	death_last_col_value	= NaN;
	
	% is function called with an argument? (-> nargin == 1 )
	if nargin == 1
		search_mode = true;
		display_on	= false;
		search_idx	= varargin{1};
	else
		% default function call
		search_mode = false;
	end

	% define matrix of strings (names) for all possible policies
	policies_str = {'Extreme Eco-Tax','Mob. Detox Day','Return Deposit'; ... % these are possible options in round 1
		'School RepCafe','Phone Subscr','1-Phone Law'; ... % these are those for round 2 and so on
		'BYOD','Youth Protect','Serv Contract'; ...
		'Don''t Ph and Dr','Sust Devices Act','Recycle Bonus'; ...
		'No Exploit','Consume Limit','Bio Phone'; ...
		'Limit Footprint','Unlock','Closed-loop'; ...
		};
% 		policies_str = {'Extreme Eco-Tax','Mob. Detox Day',; ... % these are possible options in round 1
% 		'School RepCafe','Phone Subscr'; ... % these are those for round 2 and so on
% 		'BYOD','Youth Protect'; ...
% 		'Don''t Ph and Dr','Sust Devices Act'; ...
% 		'No Exploit','Consume Limit'; ...
% 		'Limit Footprint','Unlock'; ...
% 		};
	policies_str = cellfun(@(x) pad(x(1:min(end, max_text_length)), max_text_length, 'right'), policies_str, 'UniformOutput', false);
	
	% define the outcomes for each of the above options
	% each {x,y,z}-tripel is for one option and contains the changes to
	% {happiness, circularity, money}
	policies_changes = {{-2,2,2},{0,1,0},{-1,1,0}; ... % again, this is for round 1 options
		{0,1,0},{1,-2,1},{-2,1,-1}; ... % round 2 options ....
		{0,1,-1},{-1,1,-1},{1,1,0}; ...
		{-1,0,0},{0,1,0},{1,-1,0}; ...
		{1,1,0},{-2,2,-1},{0,1,-1}; ...
		{-1,1,0},{1,1,-1},{0,1,0}; ...
		};

	% instead of having a fixed (constant) value for the number of options,
	% just count the number of entries per row. Note: this assumes that the
	% number does not change with the rounds. 
	% Now the number of options is always 3 in each round.
	nof_policies_options	= size(policies_str,2);

	
	% repeat the names definitions and the definition of the respective
	% changes for the events. It's like the policies, but there might
	% happen an event or not (at 3 specific rounds during a game), and each
	% event is independent of the other potential events. 
	% In case "no event was triggered" the option in this program is "No
	% Event #" (# stands for the potential event number)
	% Note: actually this covers two options at once: the first is (in the
	% game) the randomly chosen event (Fire, Collapse, and MiniTEc and also
	% No Event can happen). If an event had occured, the user can choose to
	% react to it in two ways, that's what is meant with Fire:1 and Fire:2
	% for example. So, there are 7 possible selections in each round when
	% an event can occur.
	event_str = {'No Event 1', 'Fire:1', 'Fire:2', 'Collapse:1', 'Collapse:2', 'MiniTec:1', 'MiniTec:2' ; ... % events in the first event round
		'No Event 2', 'NewPhone:1', 'NewPhone:2', 'PriceDrop:1', 'PriceDrop:2', 'GlobChipCris:1', 'GlobChipCris:2'; ...
		'No Event 3', 'ToxWaste:1', 'ToxWaste:2', 'DataTheft:1', 'DataTheft:2', 'GlobalRecess:1', 'GlobalRecess:2' ...
		};

	event_str = cellfun(@(x) pad(x(1:min(end, max_text_length)), max_text_length, 'right'), event_str, 'UniformOutput', false);
	
	event_changes = {{0;0;0},{0;0;-1},{0;-1;0},{0;0;-1},{-1;-1;0},{0;0;-1},{0;1;-1}; ...
		{0;0;0},{1;-1;1},{-1;0;0},{1;-1;-1},{-1;0;1},{-1;2;-1},{0;0;-2}; ...
		{0;0;0},{-1;0;-1},{0;-1;0},{-1;-1;0},{1;1;-1},{0;2;-1},{0;0;-1} ...
		};

	nof_event_options	= size(event_str,2);

	
	% and again, now for the technologies
	% Note: The user has the option to choose how much money he wants to
	% spent to get some technology. All four possible user inputs (0, 1, 2,
	% or 3 technologies) must be examined in this program.
	% Note 2: If the user pays e.g. only 2 money, the third technology
	% option will be automatically "No tech 3". 
	tech_str = {'No Tech 1','Magnetic Break-A','New 3-Diam Glass','LEO Signal Mesh';
		'No Tech 2','Smart Bins','Reg. Port Matrix','Self-Destruct'; ...
		'No Tech 3','Mod Smartphone','New Self-Charging','Smart-Shattering'};
	
	tech_str = cellfun(@(x) pad(x(1:min(end, max_text_length)), max_text_length, 'right'), tech_str, 'UniformOutput', false);
	
	tech_changes = {{0;0;0},{1;1;0},{2;1;0},{1;0;0}; ...
		{0;0;0},{0;1;0},{1;1;0},{1;0;0}; ...
		{0;0;0},{1;2;0},{1;0;1},{0;1;0}; ...
		};

	nof_tech_options	= size(tech_str,2);

	% --- okay, the definitions are set now
	
	% In order to set up a matrix of all (theoretical) possible options I
	% am using a Matlab function "fullfact" (full factorization) which
	% needs the number of options in every step; where each round contains
	% two steps (depending of the specific round)
	comb_vec = [nof_policies_options nof_event_options ... % runde 1
		nof_policies_options nof_tech_options  ... % runde 2
		nof_policies_options nof_event_options ... % runde 3
		nof_policies_options nof_event_options ... % runde 4
		nof_policies_options nof_tech_options  ... % runde 5
		nof_policies_options nof_tech_options  ... % runde 6
		];

	% ========================================================================
	% --- start of loop to check the outcome for every step
	
	% CHANGE: Reverse order, we begin with the last step (because Matlab
	
	% ======= this is step 1 (first policy choice which occurs in round 1)
	nof_options		= comb_vec(1); % here, this is the number of policy options in round 1 (= step 1)
	combinations	= fullfact(nof_options); % "fullfact" is easy here: if there are three options, 
	% the possible options are = 1, 2 or 3

	% Now, check the outcome for the next steps (remember, each round
	% contains (up to) two steps (e.g. one choice of policy and one choice of an
	% event), that's why this loop starts at step 2 and runs up to 12. 
	
	% What happens here is to build up a matrix of all possible selection.
	% If there are three options in step 1 (1,2,3) and the next step
	% offers (for the sake of simplicity) only two options, this would result in the following
	% matrix of combinations (wich is stored in the variable
	% "combinations")
	% selected option in step 1 - selected option in step 2
	%			1						1
	%			1						2
	%			2						1
	%			2						2
	%			3						1
	%			3						2
	% -> Every row is a unique sequence of steps (up to 12 if three technologies are paid)

	for i = 2:12
		
		% For explanation read the comment in the "else" section first
		
		if i == 10
			last_tech_col = 4; % that was the round with the first possible technology
			combinations_wo_Tech = find(combinations(:,last_tech_col) == 1); % tech == 1 => without Tech
			% this contains all combinations (that part of the matrix where
			% the technology 1 was "Not Tech"
			new_combs1 = [combinations(combinations_wo_Tech,:), repmat(1,numel(combinations_wo_Tech),1)];
			% in this step (10) we don't have to repeat the recent matrix
			% of combinations with the options for a next technology in
			% round 10, but still we have to add the option 1 ("No Tech 2")
			% to the matrix.
			% Now, find all rows where there was a Technology in round 4
			combinations_w_Tech = find(combinations(:,last_tech_col) > 1);
			% This part (these rows) of the combinations matrix we must be
			% repeated for every possible option for Technology 2 (including
			% option 1, "No Tech 2". Note: Therefore "new_combs2" is much
			% bigger
			new_combs2 = [repmat(combinations(combinations_w_Tech,:),nof_tech_options ,1), ...
				sort(repmat([1:nof_tech_options]',numel(combinations_w_Tech),1))];
			% Now, combine both parts
			combinations = [new_combs1 ; new_combs2];

		elseif i == 12
			% See comments in IF-Clause i==10
			% except that this clause has to separate the parts of the
			% matrix where "No Tech 2" was the outcome (which is
			% automatically true if "No Tech 1" was chosen) and the
			% remaining rest.
			last_tech_col = 10;
			combinations_wo_Tech = find(combinations(:,last_tech_col) == 1); % tech == 1 => without Tech
			new_combs1 = [combinations(combinations_wo_Tech,:), repmat(1,numel(combinations_wo_Tech),1)];

			combinations_w_Tech = find(combinations(:,last_tech_col)>1);

			new_combs2 = [repmat(combinations(combinations_w_Tech,:),nof_tech_options ,1), ...
				sort(repmat([1:nof_tech_options]',numel(combinations_w_Tech),1))];
			
			combinations = [new_combs1 ; new_combs2];

		else
			% This is the default case (but had to be placed last)
			% (Note: Matlab leaves the IF-Loop when the first true clause
			% was found (or "else") and executed)
			
			% After step 1 
			old_size			= size(combinations,1); %& remember the current count of rows
			nof_new_choices		= comb_vec(i); % this is how many options are added by the actual step
			combinations_mul	= repmat(combinations,nof_new_choices,1); % the last matrix of combinations ...
			% must be multiplied (and repeated) by the number of new
			% options. See the comment in front of this loop. At step 1 the
			% matrix contained just "1 2 3" (in a column), step 2 offered
			% (in the example) two more options, so the matrix must now
			% contain the options of step 1 twice to reflect all
			% combinations with the next step's options ... which are added
			% here:
			combinations		= [combinations_mul sort(repmat([1:nof_new_choices]',old_size,1))];
			% Policies and events are easy, but the actual number of
			% steps depends on the user choice at the start of the game:
			% How much money does he wants to spent in technologies. Now,
			% this is the reason for the other IF-clauses.

			
% TODO: It seems that the user actually have only the choice
% between 1, 2 or 3 technologies, not 0. I've to check the code, but I think
% I did it correctly

		end
		
		% To prevent false data, just clear the variables for the next step
		clear combinations_* new_comb* combinations_mul nof_new_choices
		
	end % consider/execute next step's options

	% the number of all theoretical combinations is now just the number of
	% rows of this matrix "combinations". Note: Because "death" is possible
	% some (actually many) combinations are not possible to reach (e.g. if
	% the selection of the first steps 
	nof_combinations = size(combinations,1);

	combinations	= sortrows(combinations,1:size(combinations,2)); % reverse order of sorting
	
	%display_on = true;
	
%nof_combinations = 15000; % debug	
	
	circle_vec	= zeros(nof_combinations,1);
	happy_vec	= zeros(nof_combinations,1);
	money_vec	= zeros(nof_combinations,1);
	
	death_cell	= cell(nof_combinations,1);
	
	% This is for time information
	t_start = tic;
	
	
	% Now the actual works just begins: Execute what happens in each step
	% in all rows of the combination's matrix
	
	for comb_idx = 1:nof_combinations

		% this code results in status information now and then
		if mod(comb_idx,10000) == 9999
			time = toc(t_start)/60;
			ratio = comb_idx/nof_combinations;
			still_time = time / ratio -time;
			disp([num2str(round(ratio*100,3)) ' % (elapsed time: ' num2str(round(time,3)) ' min, still expected: ' num2str(round(still_time,1)) ' min)'])
		end
		
		% ------------------------------------------------------------------
		% ---- begin with setting the start values
		mess_strings	= cell(max_mstrings,1); % this is used for some output
		mess_idx		= 1;

		policies_idx	= 1; % all three types of options start with their first "round"
		events_idx		= 1;
		tech_idx		= 1;
		
		% set the game variables
		happy			= happy_start;
		circularity		= circularity_start;
		money			= money_start  - sum(int8(combinations(comb_idx,[4 10 12]) > 1));
		% money: start value depends on the user's choice on how many
		% technologies he would like to research
		% ------------------------------------------------------------------
		
		
		% Extract the choices for all steps in this combination (= row in
		% the big matrix)
		choices	= combinations(comb_idx,:);
		
		% Skip this combination if the recent "past" of this very combination already resulted in "death" 
		% (this "path" must be cleared of possible spaces - old bug?)
		% first check if there are any death entries at all, then look for
		% the actual path
		%if death > 0 && ~isempty(cellstrfind(death_cell(1:death),strrep(num2str(choices),' ',''), 'matchstart','matchcase')) % only check the actual death combinations 
		if  death > 0 && ~isnan(death_occured_in) && choices(death_occured_in) == death_last_col_value
			% use option matchcase, since we have to compare digits only -> faster
			skip = skip + 1; % count the skipped combinations (this leads to the difference of theoretical and actual possible combinations)
			if display_on
				disp('.')
			end
		else

			% Now, cycle through all steps
			for col_idx = 1:numel(choices)

				if ~isempty(intersect(col_idx,[1:2:12])) % every odd step is a policy step

					mess_strings{mess_idx} = [' & ' policies_str{policies_idx,choices(col_idx)} ]; % for output and reference, what is the actual policy here?
					mess_idx = mess_idx + 1;
					
					results = policies_changes{policies_idx,choices(col_idx)}; % get the outcome (happy,circularity,money) for this policy option

					policies_idx = policies_idx + 1; % after this step was execute move on to the next available options for the next policiy step

				elseif ~isempty(intersect(col_idx,[2 6 8])) % these are the possible event steps
					
					mess_strings{mess_idx} = [' & ' event_str{events_idx,choices(col_idx)} ];
					mess_idx = mess_idx + 1;
					
					results = event_changes{events_idx,choices(col_idx)};

					events_idx = events_idx + 1;

				elseif ~isempty(intersect(col_idx,[4 10 12])) % and here the possible technologies are processed
					
					mess_strings{mess_idx} = [' & ' tech_str{tech_idx,choices(col_idx)} ];
					mess_idx = mess_idx + 1;
					
					results = tech_changes{tech_idx,choices(col_idx)};

					tech_idx = tech_idx + 1;
				end

				% Now apply the outcome of the actual step to the game
				% variables
				happy		= happy + results{1};
				circularity = max([0,circularity + results{2}]); % this variable shall never be below zero
				money		= money + results{3};

				if happy < 1 % that's bad, this leads to "death"
					happy = 0;
					death = death + 1;
					death_cell(death) = {strrep(num2str(choices(1:col_idx)),' ','')}; % store the combination
					death_occured_in = col_idx;
					death_last_col_value = choices(col_idx);
					mess_strings{mess_idx} = ' ... DEATH (happy)';
					mess_idx = mess_idx + 1;
					break 
				end
				
				if money < 1 % also bad, leads to "death", too
					money = 0;
					death = death + 1;
					death_cell(death) = {strrep(num2str(choices(1:col_idx)),' ','')};
					death_occured_in = col_idx;
					death_last_col_value = choices(col_idx);
					mess_strings{mess_idx} = ' ... DEATH (money)';
					mess_idx = mess_idx + 1;
					break
				end
				
				death_occured_in		= NaN;
				death_last_col_value	= NaN;
				
				mess_strings{1} = mess_strings{1}(4:end); % delete layout characters in front 
				

			end % of game choices (single steps) for one playthrough

			mess_str = strjoin(mess_strings(1:mess_idx-1), ''); % merge alle message sub strings
			
			if happy > 0 && money > 0 % if not "dead" update game variable "history"
				circle_vec(comb_idx)	= circularity;
				happy_vec(comb_idx)		= happy;
				money_vec(comb_idx)		= money;

			else % if dead, update history with "NaN"
				circle_vec(comb_idx)	= NaN;
				happy_vec(comb_idx)		= NaN;
				money_vec(comb_idx)		= NaN;
			end
			
			% output if search mode had a hit or the time is right for a
			% new status information
			if display_on || search_mode && comb_idx == search_idx
				if happy == 0
					disp(['final (' num2str(comb_idx,'%05d') '): happy = --, circularity = --,' ...
						' money = -- <- ' mess_str ])
				else
					disp(['final (' num2str(comb_idx,'%05d') '): happy = ' num2str(happy,'%02d') ', circularity = ' num2str(circularity,'%+0g') ...
						', money = ' num2str(money,'%+0g') ' <- ' mess_str ])
				end
				disp('')
			end
		end
	end % next combination
	
	time = toc(t_start)/60;
	disp(['total elapsed time: ' num2str(round(time,3)) ' min'])

	% calculate some more metrics
	%sum_vec		= happy_vec + circle_vec;
	%diff_vec	= abs(happy_vec - circle_vec);
	%metric_vec	= 2*((happy_vec + circle_vec) - diff_vec)  + money_vec;
	metric_vec	= 2.5*circle_vec + 1.5 * happy_vec + money_vec;
	
	% ---- show statistics ------------
	disp(' ')
	disp(['Combinations (theoretical): ' num2str(nof_combinations)]) % all possible theoretical combinations 
	disp(['Early terminations: ' num2str(death)]) % death happened in that many combinations (including also all combinations that are possible after the "death" event
	disp(['"Lucky Playthroughs: ' num2str(nof_combinations - death - skip)]) % number of successful playthroughs
	disp(['Minimal Happiness: ' num2str(min(happy_vec))])
	disp(['Maximal Happiness: ' num2str(max(happy_vec))])
	disp(['Minimal Circularity: ' num2str(min(circle_vec))])
	disp(['Maximal Circularity: ' num2str(max(circle_vec))])
	%disp(['Minimale Summe (H+C): ' num2str(min(sum_vec))])
	%disp(['Maximale Summe (H+C): ' num2str(max(sum_vec))])
	%disp(['Minimale Differenz (H-C): ' num2str(min(diff_vec))])
	%disp(['Maximale Differenz (H-C): ' num2str(max(diff_vec))])
	disp(['Minimal Money: ' num2str(min(money_vec))])
	disp(['Maximal Money: ' num2str(max(money_vec))])
	disp(['Minimal Metric: ' num2str(min(metric_vec))])
	disp(['Maximal Metric: ' num2str(max(metric_vec))])

	%disp(['"Übersprungene Kombinationen: ' num2str(skip)]) % skipped combinations

	
	% ---- merge all results into one structured variable --
% 	results = struct('happy',{happy_vec}, 'circularity',{circle_vec},'summe',{sum_vec}, 'difference', {diff_vec}, ...
% 		'money', {money_vec}, 'metric', {metric_vec}, 'nof_comb',{nof_combinations}, 'death', {death}, 'combinations', combinations);

	% ---- save whole workspace
	% save('.\Bianca_Daten.mat')

	% ---- clear workspace
	clear *_idx *_start nof_com* nof_* old_size time i circularity differ happy display_on last_tech_col
	clear mess_str metric money new_* ratio search_mode still_time varargin


	% ------- Visual Output (histograms) ---------
	histogram(metric_vec,'BinMethod','Integers');
	
% 	j = 1;
% 	for i = fieldnames(results)'
% 		t = i{:};
% 		if j == 6 % || j < 7 % || j > 8 - other histograms were used to evaluate a good metric
% 			figure,
% 			histogram(results.(t),'BinMethod','Integers');
% 			title(t);
% 			disp(['"' t ': ' num2str(min(results.(t))) ' bis ' num2str(max(results.(t)))]);
% % 		elseif j < 9
% % 			disp(['"' t ': ' num2str(results.(t)) ]);
% 		end
% 		j = j + 1;
% 	end
	clear j t

end

