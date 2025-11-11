! Reference Fortran code for SoilTemperatureMod thermal conductivity calculation
! This is the CORRECT implementation that the buggy Python code should match

subroutine calculate_soil_thermal_conductivity( &
    h2osoi_liq, h2osoi_ice, watsat, tkmg, tkdry, &
    n_columns, n_levels, tk)
    
    implicit none
    
    ! Input arguments
    integer, intent(in) :: n_columns, n_levels
    real(r8), intent(in) :: h2osoi_liq(n_columns, n_levels)
    real(r8), intent(in) :: h2osoi_ice(n_columns, n_levels)
    real(r8), intent(in) :: watsat(n_columns, n_levels)
    real(r8), intent(in) :: tkmg(n_columns, n_levels)
    real(r8), intent(in) :: tkdry(n_columns, n_levels)
    
    ! Output
    real(r8), intent(out) :: tk(n_columns, n_levels)
    
    ! Local variables
    integer :: i, j
    real(r8) :: sat
    
    ! NOTE: Fortran uses 1-based indexing!
    ! Loop over all columns (from 1 to n_columns)
    do i = 1, n_columns
        do j = 1, n_levels
            ! Calculate saturation
            sat = (h2osoi_liq(i,j) + h2osoi_ice(i,j)) / watsat(i,j)
            sat = max(0.0_r8, min(1.0_r8, sat))
            
            ! Johansen (1975) thermal conductivity model
            ! Dry conductivity + saturation-weighted difference to saturated
            tk(i,j) = tkdry(i,j) + sat * (tkmg(i,j) - tkdry(i,j))
        end do
    end do
    
end subroutine calculate_soil_thermal_conductivity


subroutine calculate_heat_capacity( &
    h2osoi_liq, h2osoi_ice, csol, dz, &
    n_columns, n_levels, cpliq, cpice, cv)
    
    implicit none
    
    ! Input arguments
    integer, intent(in) :: n_columns, n_levels
    real(r8), intent(in) :: h2osoi_liq(n_columns, n_levels)
    real(r8), intent(in) :: h2osoi_ice(n_columns, n_levels)
    real(r8), intent(in) :: csol(n_columns, n_levels)
    real(r8), intent(in) :: dz(n_columns, n_levels)
    real(r8), intent(in) :: cpliq  ! Specific heat of liquid [J/kg/K]
    real(r8), intent(in) :: cpice  ! Specific heat of ice [J/kg/K]
    
    ! Output
    real(r8), intent(out) :: cv(n_columns, n_levels)
    
    ! Local variables
    integer :: i, j
    real(r8) :: cv_soil, cv_water, cv_ice
    
    ! Loop over all columns and levels
    do i = 1, n_columns
        do j = 1, n_levels
            ! Soil solids contribution [J/m²/K]
            cv_soil = csol(i,j) * dz(i,j)
            
            ! Water contribution [J/m²/K]
            ! h2osoi_liq is in kg/m², multiply by specific heat
            cv_water = h2osoi_liq(i,j) * cpliq
            
            ! Ice contribution [J/m²/K]
            cv_ice = h2osoi_ice(i,j) * cpice
            
            ! Total volumetric heat capacity
            cv(i,j) = cv_soil + cv_water + cv_ice
        end do
    end do
    
end subroutine calculate_heat_capacity

