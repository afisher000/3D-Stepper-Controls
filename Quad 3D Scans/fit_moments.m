close all;
clearvars;
clc;

%%
quad = 1;
filename = sprintf('q%d_xyslice.csv',quad);
T = readtable(filename);

% Optimization variables
x0 = zeros(1,6);
[opt_moments, fval] = fminsearch(@(x) optimize_moments(x, T), x0);


%% Print results
opt_moments = opt_moments*1000;
moment_labels = {'Dipole x','Dipole y','Quad','Skew Quad','Sext.','Skew Sext.'};
fprintf('Quad%d Moments\n', quad);
for j=1:length(moment_labels)
    fprintf('%-10s = %.1f mT\n', moment_labels{j}, opt_moments(j));
end

%% 
function error = optimize_moments(x, T)
    Bx0 = x(1);
    By0 = x(2);
    kr  = x(3); %regular
    ks  = x(4); %skew
    mr  = x(5); %regular
    ms  = x(6); %skew
    
    Bx  = zeros(height(T),1);
    By  = zeros(height(T),1);
    x   = T.x;
    y   = T.y;
    
    % Build fields from moments
    Bx  = Bx + Bx0;
    By  = By + By0;
    Bx  = Bx + kr*T.y; By = By + kr*T.x;
    Bx  = Bx - ks*T.x; By = By + ks*T.y;
    Bx  = Bx + mr*x.*y; By = By + 0.5*mr*(x.^2-y.^2);
    Bx  = Bx - 0.5*ms*(x.^2-y.^2); By = By + ms*x.*y;
    
    error = sqrt(sum((Bx-T.Bx).^2)) + sqrt(sum((By-T.By).^2));
    error = error/(2*height(T));
end
   

