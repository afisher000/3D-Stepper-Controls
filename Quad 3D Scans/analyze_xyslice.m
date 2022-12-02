clc;
close all;
clearvars;

% filename = 'By_q2_3dscan_22-11-09.csv';
% filename = 'Bx_q1_2dscan_22-11-14.csv';
filename = 'Bx_q1_3dscan_shuntout_22-11-15.csv';
z0 = 1.5*0;
T = readtable(filename);
T.x = round(T.x, 10);
T.y = round(T.y, 10);
T.z = round(T.z, 10);
xsize = length(unique(T.x));
ysize = length(unique(T.y));
zsize = length(unique(T.z));
slice_mask = (T.z==z0);

X = reshape(T.x(slice_mask), xsize, ysize);
Y = reshape(T.y(slice_mask), xsize, ysize);
F = reshape(T.field(slice_mask), xsize, ysize);

%% Define maj/min transverse coords
if contains(filename, 'Bx')
    XYMAJ   = Y;
    XYMIN   = X;
    F       = F;
    xymaj_label = 'Y (mm)';
    xymin_label = 'X (mm)';
    field_label = 'Bx Field (T)';
else
    XYMAJ   = X';
    XYMIN   = Y';
    F       = F';
    xymaj_label = 'X (mm)';
    xymin_label = 'Y (mm)';
    field_label = 'By Field (mT)';
end

figure();
subplot(2,2,1);
    contour(Y, X, F*1000);
    title(field_label);
    xlabel(xymaj_label);
    ylabel(xymin_label);
    colorbar;
    
subplot(2,2,3);
    xymaj_unique = unique(XYMAJ);
    hold on;
    plot(xymaj_unique, F*1000);
    xlabel(xymaj_label);
    ylabel(field_label);
    
%% Compute gradient
xymaj_unique = unique(XYMAJ);
grad_fit = polyfit(xymaj_unique, F(:,(end+1)/2), 1); 
grad_comp = polyval(grad_fit, xymaj_unique);

%% 
F_nolinear = F - grad_comp;
subplot(2,2,2);
    contour(Y, X, F_nolinear*1000);
    title('Subtract gradient comp.');
    xlabel(xymaj_label);
    ylabel(xymin_label);
    colorbar;
subplot(2,2,4);
    xymin_unique = unique(XYMIN);
    hold on;
    title('Subtract gradient comp.');
    plot(xymin_unique, F_nolinear'*1000);
    xlabel(xymin_label);
    ylabel(field_label);


saveas(gcf, 'temp.jpg');











