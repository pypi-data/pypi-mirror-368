use crate::filtration::Filtration;
use crate::process::Process;
use crate::process::increment::Incrementor;
use ordered_float::OrderedFloat;

pub struct LevyProcess {
    name: String,
    coefficients: Vec<Box<dyn Fn(&Filtration, OrderedFloat<f64>, i32) -> f64>>,
    incrementors: Vec<Box<dyn Incrementor>>,
}

impl Process for LevyProcess {
    fn name(&self) -> &String {
        &self.name
    }

    fn coefficients(&self) -> &Vec<Box<dyn Fn(&Filtration, OrderedFloat<f64>, i32) -> f64>> {
        &self.coefficients
    }

    fn incrementors(&mut self) -> &mut Vec<Box<dyn Incrementor>> {
        &mut self.incrementors
    }
}

impl LevyProcess {
    pub fn new(
        name: String,
        coefficients: Vec<Box<dyn Fn(&Filtration, OrderedFloat<f64>, i32) -> f64>>,
        incrementors: Vec<Box<dyn Incrementor>>,
    ) -> Result<Self, String> {
        if coefficients.len() != incrementors.len() {
            return Err("coefficients and incrementors must have the same length".to_string());
        }
        Ok(Self {
            name,
            coefficients,
            incrementors,
        })
    }
}
