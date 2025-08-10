use pyo3::prelude::*;

#[pyfunction]
fn solve_sdvrp(
    random_seed: u32,
    time_limit: f64,
    blink_rate: f64,
    inter_operators: Vec<String>,
    intra_operators: Vec<String>,
    acceptance_rule_type: String,
    lahc_length: i32,
    sa_initial_temperature: f64,
    sa_decay: f64,
    ruin_method_type: String,
    sisrs_average_customers: i32,
    sisrs_max_length: i32,
    sisrs_split_rate: f64,
    sisrs_preserved_probability: f64,
    random_ruin_sizes: Vec<i32>,
    sorters: Vec<String>,
    sorter_values: Vec<f64>,

    capacity: i32,
    demands: Vec<i32>,
    input_format: String,
    distance_matrix: Vec<i32>,
    coord_list_x: Vec<i32>,
    coord_list_y: Vec<i32>,
) -> Vec<Vec<(i32, i32)>> {
    let result = unsafe {
        sdvrp::ffi::solve_sdvrp(
            random_seed,
            time_limit,
            blink_rate,
            inter_operators.iter().map(|x| x.as_str()).collect(),
            intra_operators.iter().map(|x| x.as_str()).collect(),
            acceptance_rule_type.as_str(),
            lahc_length,
            sa_initial_temperature,
            sa_decay,
            ruin_method_type.as_str(),
            sisrs_average_customers,
            sisrs_max_length,
            sisrs_split_rate,
            sisrs_preserved_probability,
            random_ruin_sizes,
            sorters.iter().map(|x| x.as_str()).collect(),
            sorter_values,
            capacity,
            demands,
            input_format.as_str(),
            distance_matrix,
            coord_list_x,
            coord_list_y,
        )
    };
    sdvrp::split_results(result)
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve_sdvrp, m)?)?;
    Ok(())
}
