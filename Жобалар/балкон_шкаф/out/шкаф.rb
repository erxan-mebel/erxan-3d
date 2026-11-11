# ERXAN MEBEL · Балкон шкаф — SketchUp Pro: Window > Ruby Console, paste and press Enter.
model = Sketchup.active_model
model.start_operation('Балкон шкаф', true)
mats = {
  'ЛДСП' => model.materials['ЛДСП'] || model.materials.add('ЛДСП'),
  'ХДФ' => model.materials['ХДФ'] || model.materials.add('ХДФ'),
  'Фасад' => model.materials['Фасад'] || model.materials.add('Фасад'),
}
mats['ЛДСП'].color = Sketchup::Color.new(244, 239, 232)
mats['ХДФ'].color = Sketchup::Color.new(201, 181, 153)
mats['Фасад'].color = Sketchup::Color.new(255, 255, 255)
root = model.active_entities.add_group
root.name = 'Балкон шкаф 900x2200x400'
box = lambda do |name, mat, x, y, z, dx, dy, dz|
  g = root.entities.add_group
  f = g.entities.add_face([x.mm, y.mm, z.mm], [(x + dx).mm, y.mm, z.mm], [(x + dx).mm, (y + dy).mm, z.mm], [x.mm, (y + dy).mm, z.mm])
  f.reverse! if f.normal.z < 0
  f.pushpull(dz.mm)
  g.name = name
  g.material = mats[mat]
end
box.call('Бүйір (сол)', 'ЛДСП', 0, 0, 0, 16, 397, 2200)
box.call('Бүйір (оң)', 'ЛДСП', 884, 0, 0, 16, 397, 2200)
box.call('Төбе', 'ЛДСП', 16, 0, 2184, 868, 397, 16)
box.call('Түп', 'ЛДСП', 16, 0, 80, 868, 397, 16)
box.call('Цоколь алдыңғы', 'ЛДСП', 16, 20, 0, 868, 16, 80)
box.call('Цоколь артқы', 'ЛДСП', 16, 361, 0, 868, 16, 80)
box.call('Сөре 1', 'ЛДСП', 16, 0, 500.8, 868, 377, 16)
box.call('Сөре 2', 'ЛДСП', 16, 0, 921.6, 868, 377, 16)
box.call('Сөре 3', 'ЛДСП', 16, 0, 1342.4, 868, 377, 16)
box.call('Сөре 4', 'ЛДСП', 16, 0, 1763.2, 868, 377, 16)
box.call('Артқы қабырға', 'ХДФ', 1, 397, 1, 898, 3, 2198)
box.call('Есік (сол)', 'Фасад', 2, -16, 82, 447, 16, 2116)
box.call('Есік (оң)', 'Фасад', 451, -16, 82, 447, 16, 2116)
model.commit_operation
Sketchup.active_model.active_view.zoom_extents
