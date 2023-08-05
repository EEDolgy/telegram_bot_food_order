function addDishToOrder(date, category, amount, dishName, weekDay){
    if (date in localStorage){
        dishes = JSON.parse(localStorage.getItem(date));
        let hasCategory = Object.prototype.hasOwnProperty.call(dishes,
        category);
        if (hasCategory && amount == 0){
            delete dishes[category];
        } else if (amount != 0){
            let dataOrdered = {'dishName': dishName, 'amount': amount,
            'weekDay': weekDay};
            dishes[category] = dataOrdered;
        }
        let dishesString = JSON.stringify(dishes);
        if (dishesString == '{}'){
            localStorage.removeItem(date)
        }
        else {
            localStorage.setItem(date, dishesString);
        }
    }
    else {
        if (amount != 0){
            let dishes = {};
            let dataOrdered = {'dishName': dishName, 'amount': amount,
            'weekDay': weekDay};
            dishes[category] = dataOrdered;
            localStorage.setItem(date, JSON.stringify(dishes));
        }
    }
}

function handleFormSubmit(event) {
  event.preventDefault();
  console.log('Отправка!')
  const { elements } = applicantForm;

  Array.from(elements).forEach((element) => {
      const { name, value } = element
      localStorage.setItem(name, value)
  })
  console.log(localStorage);

  alert("Данные сохранены!");
}

const applicantForm = document.getElementById('user-info')
applicantForm.addEventListener('submit', handleFormSubmit)

