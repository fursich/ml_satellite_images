require 'mini_magick'

# start_date = DateTime.new(2013, 1, 1,  0, 0, 0)
MAX_ERROR_COUNT = 3
DELAY_PER_TRIAL = 20

start_date = DateTime.new(2013, 1, 1, 9, 0, 0)
end_date   = DateTime.new(2013, 3, 4, 23, 0, 1)
# start_date = DateTime.new(2018, 6, 26, 9, 0, 0)
# end_date   = DateTime.new(2019, 2, 1, 23, 0, 1)

base_url = "https://storage.tenki.jp/archive/satellite/%s/japan-near-small.jpg"
base_filename = 'images2/%s.jpg'
base_cropped_filename = 'crop2/%s.jpg'

start_date.step(end_date, step=0.5) do |date|

  error_count = 0
  original_date = date

  loop do
    if error_count >  MAX_ERROR_COUNT
      puts "gave up requesting image on #{original_date} after #{MAX_ERROR_COUNT} trials."
      break
    end

    str = date.strftime('%Y/%m/%d/%H/00/00')
    url = base_url % str
    filename         = base_filename % str.gsub('/', '_')
    cropped_filename = base_cropped_filename % str.gsub('/', '_')

    begin
      image = MiniMagick::Image.open(url)
    rescue OpenURI::HTTPError => e
      puts "#{e.inspect} occured while requesting an image for #{str}"
      error_count += 1
      date += 1.0/24 # try with +1 hour
      next
    end

    image.write(filename)
    image.shave('20x20') # shaving image
    image.colorspace 'LinearGray'
    image.write(cropped_filename)
    break
  end
  sleep DELAY_PER_TRIAL
end

