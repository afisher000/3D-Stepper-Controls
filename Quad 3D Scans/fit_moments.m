close all;
clearvars;
% clc;

%%

filename = 'q1_xyslice_fine.csv';
filename = 'Bx_q1_3dscan_shuntout_22-11-15.csv';



T2 = readtable(filename);

scn = (T2.z==0);
T.x = T2.x(scn);
T.y = T2.y(scn);
T.Bx = T2.field(scn);
% T.By = T.field; 

if contains(filename, 'q1')
    quad = 1;
else 
    quad = 2;
end

% Optimization variables
x0 = zeros(1,6);
components = 'bx';
[opt_moments, fval] = fminsearch(@(x) optimize_moments(x, T, components), x0);


%% Print results
opt_moments = opt_moments*1000;
moment_labels = {'Dipole x','Dipole y','Quad','Skew Quad','Sext.','Skew Sext.'};
units = {'mT','mT','mT/mm','mT/mm','mT/mm^2','mT/mm^2'};
fprintf('Quad%d Moments for %s component(s)\n', quad, components);
for j=1:length(moment_labels)
    fprintf('%-10s = %.1f %s\n', moment_labels{j}, opt_moments(j), units{j});
end

%% 
function error = optimize_moments(x, T, components)
    Bx0 = x(1);
    By0 = x(2);
    kr  = x(3); %regular
    ks  = x(4); %skew
    mr  = x(5); %regular
    ms  = x(6); %skew
    
    x   = T.x;
    y   = T.y;
    
    error = 0;
    if contains(components, 'bx')
        Bx  = zeros(length(T.x),1);
        Bx  = Bx + Bx0;
        Bx  = Bx + kr*T.y;
        Bx  = Bx - ks*T.x;
        Bx  = Bx + mr*x.*y; 
        Bx  = Bx - 0.5*ms*(x.^2-y.^2); 
        error = error + sqrt(sum((Bx-T.Bx).^2))/length(T.x);
        if ~contains(components, 'by')
           error = error + abs(By0); 
        end
    end
    if contains(components, 'by')
        By  = zeros(height(T),1);
        By  = By + By0;
        By = By + kr*T.x;
        By = By + ks*T.y;
        By = By + 0.5*mr*(x.^2-y.^2);
        By = By + ms*x.*y;
        error = error + sqrt(sum((By-T.By).^2))/length(T.x);
        if ~contains(components, 'bx')
           error = error + abs(Bx0); 
        end
    end
end
   


