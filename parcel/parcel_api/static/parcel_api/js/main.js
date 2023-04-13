const {
  colors,
  CssBaseline,
  ThemeProvider,
  Typography,
  Container,
  createTheme,
  Box,
  SvgIcon,
  Button,
  Link,
  Stack,
  FormControl,
  Input,
  InputLabel,
  FormHelperText,
  Autocomplete,
  TextField,
  FormGroup
} = MaterialUI;

const {
  useState,
  useCallback,
  useEffect
} = React

const csrf_token = () => {
  return document.getElementById('csrftoken').value
}

// Create a theme instance.
const theme = createTheme({
  palette: {
    primary: {
      main: '#556cd6',
    },
    secondary: {
      main: '#19857b',
    },
    error: {
      main: colors.red.A400,
    },
  },
});


function ParcelCreateForm({ createParcel, parcelTypes }) {

  const [name, setName] = useState('Кружка "ООО Дельта"')
  const [weight, setWeigth] = useState(0.3)
  const [parcel_price, setPrice] = useState(3)
  const [type, setType] = useState(null)

  return (
    <Stack
      component="form"
      autoComplete="off"
      spacing={1}
      mt={2}
    >
      <FormControl variant="standard" required={true}>
        <InputLabel htmlFor="create-form__name">Название</InputLabel>
        <Input
          id="create-form__name"
          defaultValue={name}
          onChange={e => setName(e.target.value)}
        />
        <FormHelperText>Название посылки</FormHelperText>
      </FormControl>
      <FormControl variant="standard" required={true}>
        <InputLabel htmlFor="create-form__weight">Вес</InputLabel>
        <Input
          id="create-form__weight"
          defaultValue={weight}
          onChange={e => setWeigth(e.target.value)}
          inputprops={{
            inputProps: { min: 0 }
          }}
        />
        <FormHelperText>Вес посылки в кг</FormHelperText>
      </FormControl>
      <FormControl variant="standard" required={true}>
        <InputLabel htmlFor="create-form__parcel_price">Стоимость</InputLabel>
        <Input
          id="create-form__parcel_price"
          defaultValue={parcel_price}
          onChange={e => setPrice(e.target.value)}
          inputprops={{
            inputProps: { min: 0 }
          }}
        />
        <FormHelperText>Стоимость содержимого посылки в $</FormHelperText>
      </FormControl>
      <FormControl variant="standard" required={true}>
        <Autocomplete
          id="create-form__type"
          options={parcelTypes}
          getOptionLabel={(option) => option.name}
          value={type}
          onChange={(e, newValue) => setType(newValue)}
          renderInput={params => (
            <TextField {...params} label="Тип посылки" variant="standard" />
          )}
        />
        <FormHelperText>Тип посылки</FormHelperText>
      </FormControl>
      <Button
        onClick={e => createParcel(
          { name, weight, parcel_price, type, deliver_price: 'Не рассчитано' }
        )}
      // onClick={e => createParcel({ name, weight, parcel_price, type })}
      >Оформить посылку</Button>
    </Stack>
  )
}


function DebugUpdate() {
  const debug_update = async () => {
    const url = document.getElementById('update_prices').value
    const res = await fetch(url, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token()
      }
    })
  }

  return (
    <Stack>
      <Button onClick={e => debug_update()} variant="contained">Debug update</Button>
    </Stack>
  )
}


function ParcelsRetrieveItem({
  type, name, weight, parcel_price, deliver_price,
  id, show_id = false, mb = 0 }) {
  return (
    <Stack mb={mb} spacing={1}>
      {show_id &&
        <TextField
          disabled
          variant="outlined"
          label="Код посылки"
          value={id}
        />}
      <TextField
        disabled
        variant="outlined"
        label="Название посылки"
        value={name}
      />
      <TextField
        disabled
        variant="outlined"
        label="Вес содержимого посылки"
        value={weight}
      />
      <TextField
        disabled
        variant="outlined"
        label="Стоимость товара ($)"
        value={parcel_price}
      />
      <TextField
        disabled
        variant="outlined"
        label="Тип товара"
        value={type}
      />
      <TextField
        disabled
        variant="outlined"
        label="Стоимость доставки (₽)"
        value={deliver_price}
      />
    </Stack>
  )
}

function ParcelsList({ parcels }) {
  console.log(parcels)
  return (
    <Stack>
      <Typography mb={4} mt={2} align="center">Список посылок</Typography>
      {parcels.map(v =>
        <ParcelsRetrieveItem mb={8} key={v.id} show_id={true} {...v} />
      )}
    </Stack>
  )
}

function ParcelsRetrieve() {
  const [uuid, setUuid] = useState('')
  const [parcel, setParcel] = useState({
    type: ' ',
    name: ' ',
    weight: 0,
    parcel_price: 0,
    deliver_price: 0
  })

  const getParcelDetails = useCallback(async (id) => {
    const url = document.getElementById('parcel-detail').value.slice(0, -2) + id
    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    if (res.status === 200) {
      const data = await res.json()
      setParcel(data)
    }
  }, [setParcel])

  return (
    <Stack mt={12}>
      <FormControl
        variant="standard"
        required={true}
      >
        <InputLabel htmlFor="retrieve-form__nauuid">UUID посылки</InputLabel>
        <Input
          id="retrieve-form__uuid"
          defaultValue={uuid}
          onChange={e => setUuid(e.target.value)}
        />
        <FormHelperText>Код посылки</FormHelperText>
        <Stack mb={2}>
          <Button
            onClick={e => getParcelDetails(uuid)}
          >
            Получить информацию о посылке
          </Button>
        </Stack>
      </FormControl>
      <ParcelsRetrieveItem {...parcel} />
    </Stack>
  )
}

function App() {
  const [parcels, setParcels] = useState([])
  const [parcelTypes, setParcelTypes] = useState([{ id: 1, name: "JoJo" }])

  const addParcel = useCallback(async parcel_data => {
    const url = document.getElementById('register_parcel').value
    const form_data = { ...parcel_data }
    form_data['type'] = form_data['type'].id
    const deliver_price = form_data.deliver_price
    const res = await fetch(url, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token()
      },
      body: JSON.stringify(form_data)
    })
    if (res.status === 201) {
      const data = await res.json()
      data.deliver_price = deliver_price
      setParcels([data, ...parcels])
    }
  }, [parcels, setParcels])

  useEffect(() => {
    const func = async () => {
      const url = document.getElementById('parcel_types').value
      const res = await fetch(url, {
        method: "GET",
        headers: {
          'Content-Type': 'application/json'
        }
      })
      if (res.status === 200) {
        const data = await res.json()
        setParcelTypes(data['results'])
      }
    }
    func()
  }, [setParcelTypes])

  useEffect(() => {
    const func = async () => {
      const url = document.getElementById('parcel-list').value
      const res = await fetch(url, {
        method: "GET",
        headers: {
          'Content-Type': 'application/json'
        }
      })
      if (res.status === 200) {
        const data = await res.json()
        setParcels(data['results'])
      }
    }
    func()
  }, [setParcels])

  return (
    <Container maxWidth="sm" >
      <Stack spacing={2}>
        <DebugUpdate />
        <ParcelCreateForm createParcel={addParcel} parcelTypes={parcelTypes} />
        <ParcelsRetrieve />
        <ParcelsList parcels={parcels} />
      </Stack>
    </Container>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ThemeProvider theme={theme}>
    {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
    <CssBaseline />
    <App />
  </ThemeProvider>,
);